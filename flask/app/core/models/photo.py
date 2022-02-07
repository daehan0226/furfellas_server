import os
import time
import traceback
from datetime import datetime
from dateutil.relativedelta import relativedelta
from threading import Lock, Thread

import sqlalchemy
from sqlalchemy.orm import relationship
from dotenv import load_dotenv


from app.core.file_manager import FileManager
from app.core.database import (
    db,
    association_table_photo_action,
    association_table_photo_pet,
)
from app.core.models import BaseModel
from app.core.database import get_db_session
from app.core.google_drive_api import GoogleDrive
from app.core.utils import convert_to_datetime, convert_str_ids_to_int_ids_tuple


APP_ROOT = os.path.join(os.path.dirname(__file__), "..")
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)


REMOVE_IMAGE_INTERVAL_SECONDS = int(os.getenv("REMOVE_IMAGE_INTERVAL_HOURS")) * 3600


lock = Lock()


class Photo(BaseModel):
    __tablename__ = "photo"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    image_id = db.Column(db.String(100))
    filename = db.Column(db.String(100), unique=True, nullable=False)
    upload_status = db.Column(db.Integer, default=0)
    location_id = db.Column(
        db.Integer, db.ForeignKey("location.id", ondelete="SET NULL")
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    create_datetime = db.Column(db.DateTime, default=datetime.now())
    upload_datetime = db.Column(db.DateTime, default=datetime.now())

    actions = relationship(
        "Action", secondary=association_table_photo_action, back_populates="photos"
    )

    pets = relationship(
        "Pet", secondary=association_table_photo_pet, back_populates="photos"
    )

    def __init__(self, **columns):
        self.description = columns["description"]
        self.image_id = ""
        self.location_id = columns["location_id"]
        self.user_id = columns["user_id"]
        self.create_datetime = columns["create_datetime"]
        self.filename = columns["filename"]

    @classmethod
    def insert_image_id(cls, photo_id, image_id):
        photo = cls.get_by_id(photo_id)
        photo.image_id = image_id
        db.session.commit()

    def _upload_status_str(self, status_id):
        return Photo._get_upload_status_list()[status_id]

    @staticmethod
    def _get_upload_status_list():
        return ["waiting", "uploading", "uploaded", "fail"]

    @classmethod
    def get_upload_status_id(cls, status):
        status_list = cls._get_upload_status_list()
        return status_list.index(status)

    def __repr__(self):
        return self._repr(
            id=self.id,
            description=self.description,
            image_id=self.image_id,
            location_id=self.location_id,
            user_id=self.user_id,
            create_datetime=self.create_datetime,
            upload_datetime=self.upload_datetime,
        )

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        from app.core.models import Location, UserProfile

        return {
            "id": self.id,
            "description": self.description,
            "image_id": self.image_id,
            "user": UserProfile.query.get(self.user_id).serialize,
            "create_datetime": self.create_datetime.isoformat(),
            "upload_datetime": self.upload_datetime.isoformat(),
            "upload_status": self._upload_status_str(self.upload_status),
            "location": Location.query.get(self.location_id).serialize,
            "thumbnail": f"https://drive.google.com/thumbnail?id={self.image_id}"
            if self.image_id
            else "",
            "original": f"https://drive.google.com/uc?export=view&id={self.image_id}"
            if self.image_id
            else "",
            "actions": [action.serialize for action in self.actions],
            "pets": [pet.serialize for pet in self.pets],
        }

    @classmethod
    def remove_uploaded_file(cls):
        while True:
            try:
                db_scoped_session = get_db_session()
                db_session = db_scoped_session()

                tmp_files = FileManager.get_tmp_files()

                for tmp_file in tmp_files:
                    try:
                        photo = (
                            db_session.query(cls)
                            .filter_by(filename=str(tmp_file))
                            .one()
                        )
                        if photo.upload_status == cls.get_upload_status_id("uploaded"):
                            FileManager.remove(filename=tmp_file)
                    except Exception as e:
                        FileManager.remove(filename=tmp_file)
            except Exception as e:
                print(e)
            finally:
                db_scoped_session.remove()
                time.sleep(REMOVE_IMAGE_INTERVAL_SECONDS)

    @classmethod
    def get_photos_to_upload(cls):
        db_scoped_session = get_db_session()
        db_session = db_scoped_session()
        photos = db_session.query(cls).filter_by(
            upload_status=cls.get_upload_status_id("waiting")
        )
        db_scoped_session.remove()
        return photos

    @classmethod
    def upload_files(cls, filenames=None):
        if filenames is None:
            photos = cls.get_photos_to_upload()
            filenames = [photo.filename for photo in photos]
            # filenames = FileManager.get_tmp_files()

        if filenames:
            folder_id = GoogleDrive.get_file_id_by_name("furfellas")
            file_info = [(folder_id, filename) for filename in filenames]
            # p = ThreadPool(4)
            # p.starmap(upload, file_info)

            for file in file_info:
                folder_id, file_name = file
                upload_thread = Thread(
                    target=cls.upload, args=(folder_id, file_name), daemon=True
                )
                upload_thread.start()

    @classmethod
    def upload(cls, folder_id, filename):
        with lock:
            db_scoped_session = get_db_session()
            db_session = db_scoped_session()
            photo = db_session.query(cls).filter_by(filename=filename).one()
            photo.upload_status = cls.get_upload_status_id("uploading")
            db_session.commit()
            try:
                photo.image_id = GoogleDrive.upload(folder_id, filename)
                photo.upload_status = cls.get_upload_status_id("uploaded")
            except:
                photo.upload_status = cls.get_upload_status_id("fail")

            db_session.commit()
            db_scoped_session.remove()

    @classmethod
    def save_photo(cls, photo_columns):
        from app.core.models import Action, Pet

        try:
            photo_columns["create_datetime"] = convert_to_datetime(
                photo_columns["create_datetime"]
            )
            photo = cls(**photo_columns)
            photo.actions = Action.get_action_model_list_from_str_action_ids(
                photo_columns["action_ids"]
            )
            photo.pets = Pet.get_pet_model_list_from_str_action_ids(
                photo_columns["pet_ids"]
            )
            return photo.create(), ""
        except sqlalchemy.exc.IntegrityError as e:
            print(e)
            return False, "Wrong location id"
        except sqlalchemy.orm.exc.FlushError as e:
            print(e)
            return False, "Wrong action id"
        except:
            traceback.print_exc()
            return False, "Something went wrong"

    @classmethod
    def update_photo(cls, photo_id, photo_columns):
        from app.core.models import Action, Pet

        try:
            photo = cls.query.get(photo_id)
            photo.location_id = photo_columns["location_id"]
            photo.description = photo_columns["description"]
            photo.create_datetime = convert_to_datetime(
                photo_columns["create_datetime"]
            )
            photo.actions = Action.get_action_model_list_from_str_action_ids(
                photo_columns["action_ids"]
            )
            photo.pets = Pet.get_pet_model_list_from_str_action_ids(
                photo_columns["pet_ids"]
            )
            db.session.commit()
            return True, ""
        except:
            traceback.print_exc()
            return False, "Something went wrong"

    @classmethod
    def get_photos(cls, args):
        from app.core.models import Action

        try:
            query = db.session.query(cls)
            query = query.filter(
                cls.upload_status == cls.get_upload_status_id("uploaded")
            )
            if location_ids := convert_str_ids_to_int_ids_tuple(args["location_ids"]):
                query = query.filter(cls.location_id.in_(location_ids))
            if action_ids := convert_str_ids_to_int_ids_tuple(args["action_ids"]):
                query = query.join(cls.actions).filter(Action.id.in_(action_ids))
            if pet_ids := convert_str_ids_to_int_ids_tuple(args["pet_ids"]):
                query = query.join(cls.pets).filter(cls.id.in_(pet_ids))
            if args["start_datetime"]:
                query = query.filter(
                    cls.create_datetime >= convert_to_datetime(args["start_datetime"])
                )
            if args["end_datetime"]:
                query = query.filter(
                    cls.create_datetime
                    <= (
                        convert_to_datetime(args["end_datetime"])
                        + relativedelta(days=1)
                    )
                )
            photos = query.all()
            return [photo.serialize for photo in photos]
        except:
            traceback.print_exc()
            return []
