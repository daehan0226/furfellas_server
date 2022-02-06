from datetime import datetime
import os
import time
import sqlalchemy
import traceback
from threading import Lock, Thread
from multiprocessing.pool import ThreadPool
from dotenv import load_dotenv

from dateutil.relativedelta import relativedelta
from flask_restplus import Namespace, reqparse, Resource
from sqlalchemy import exc
from werkzeug.datastructures import FileStorage

from core.database import db
from core.models import Photo as PhotoModel, Action as ActionModel, Pet as PetModel
from core.response import (
    CustomeResponse,
    exception_handler,
    login_required,
)
from core.utils import convert_to_datetime, convert_str_ids_to_int_ids_tuple
from core.file_manager import FileManager
from core.errors import FileSaveError
from core.database import get_db_session
from core.google_drive_api import (
    get_file_id_in_google_drvie_by_name,
    upload_to_google_drive,
)

from core.utils import set_doc_responses

APP_ROOT = os.path.join(os.path.dirname(__file__), "..")
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)


REMOVE_IMAGE_INTERVAL_SECONDS = int(os.getenv("REMOVE_IMAGE_INTERVAL_HOURS")) * 3600

api = Namespace("photos", description="Photos related operations")

lock = Lock()


def remove_uploaded_file():
    while True:
        try:
            db_scoped_session = get_db_session()
            db_session = db_scoped_session()

            tmp_files = FileManager.get_tmp_files()

            for tmp_file in tmp_files:
                try:
                    photo = (
                        db_session.query(PhotoModel)
                        .filter_by(filename=str(tmp_file))
                        .one()
                    )
                    if photo.upload_status == PhotoModel.get_upload_status_id(
                        "uploaded"
                    ):
                        FileManager.remove(tmp_file)
                except Exception as e:
                    FileManager.remove(tmp_file)
        except Exception as e:
            print(e)
        finally:
            db_scoped_session.remove()
            time.sleep(REMOVE_IMAGE_INTERVAL_SECONDS)


def get_photos_to_upload():
    db_scoped_session = get_db_session()
    db_session = db_scoped_session()
    photos = db_session.query(PhotoModel).filter_by(
        upload_status=PhotoModel.get_upload_status_id("waiting")
    )
    db_scoped_session.remove()
    return photos


def upload_files(filenames=None):
    if filenames is None:
        photos = get_photos_to_upload()
        filenames = [photo.filename for photo in photos]
        # filenames = FileManager.get_tmp_files()

    if filenames:
        folder_id = get_file_id_in_google_drvie_by_name("furfellas")
        file_info = [(folder_id, filename) for filename in filenames]
        # p = ThreadPool(4)
        # p.starmap(upload, file_info)

        for file in file_info:
            folder_id, file_name = file
            upload_thread = Thread(
                target=upload, args=(folder_id, file_name), daemon=True
            )
            upload_thread.start()


def upload(folder_id, filename):
    with lock:
        db_scoped_session = get_db_session()
        db_session = db_scoped_session()
        photo = db_session.query(PhotoModel).filter_by(filename=filename).one()
        photo.upload_status = PhotoModel.get_upload_status_id("uploading")
        db_session.commit()
        try:
            photo.image_id = upload_to_google_drive(folder_id, filename)
            photo.upload_status = PhotoModel.get_upload_status_id("uploaded")
        except:
            photo.upload_status = PhotoModel.get_upload_status_id("fail")

        db_session.commit()
        db_scoped_session.remove()


def save_photo(photo_columns):
    try:
        photo_columns["create_datetime"] = convert_to_datetime(
            photo_columns["create_datetime"]
        )
        photo = PhotoModel(**photo_columns)
        photo.actions = get_action_model_list_from_str_action_ids(
            photo_columns["action_ids"]
        )
        photo.pets = get_pet_model_list_from_str_action_ids(photo_columns["pet_ids"])
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


def get_action_model_list_from_str_action_ids(str_action_ids):
    action_ids = str_action_ids.split(",")
    return [ActionModel.query.get(int(action_id)) for action_id in action_ids]


def get_pet_model_list_from_str_action_ids(str_pet_ids):
    pet_ids = str_pet_ids.split(",")
    return [PetModel.query.get(int(pet_id)) for pet_id in pet_ids]


def update_photo(photo_id, photo_columns):
    try:
        photo = PhotoModel.query.get(photo_id)
        photo.location_id = photo_columns["location_id"]
        photo.description = photo_columns["description"]
        photo.create_datetime = convert_to_datetime(photo_columns["create_datetime"])
        photo.actions = get_action_model_list_from_str_action_ids(
            photo_columns["action_ids"]
        )
        photo.pets = get_pet_model_list_from_str_action_ids(photo_columns["pet_ids"])
        db.session.commit()
        return True, ""
    except:
        traceback.print_exc()
        return False, "Something went wrong"


def get_photos(args):
    try:
        query = db.session.query(PhotoModel)
        query = query.filter(
            PhotoModel.upload_status == PhotoModel.get_upload_status_id("uploaded")
        )
        if location_ids := convert_str_ids_to_int_ids_tuple(args["location_ids"]):
            query = query.filter(PhotoModel.location_id.in_(location_ids))
        if action_ids := convert_str_ids_to_int_ids_tuple(args["action_ids"]):
            query = query.join(PhotoModel.actions).filter(
                ActionModel.id.in_(action_ids)
            )
        if pet_ids := convert_str_ids_to_int_ids_tuple(args["pet_ids"]):
            query = query.join(PhotoModel.pets).filter(PetModel.id.in_(pet_ids))
        if args["start_datetime"]:
            query = query.filter(
                PhotoModel.create_datetime
                >= convert_to_datetime(args["start_datetime"])
            )
        if args["end_datetime"]:
            query = query.filter(
                PhotoModel.create_datetime
                <= (convert_to_datetime(args["end_datetime"]) + relativedelta(days=1))
            )
        photos = query.all()
        return [photo.serialize for photo in photos]
    except:
        traceback.print_exc()
        return []


parser_search = reqparse.RequestParser()
parser_search.add_argument("action_ids", type=str, location="args", help="action ids")

parser_search.add_argument("pet_ids", type=str, location="args", help="pet ids")
parser_search.add_argument(
    "location_ids", type=str, help="location ids", location="args"
)
parser_search.add_argument(
    "start_datetime", type=str, help="search start date", location="args"
)
parser_search.add_argument(
    "end_datetime", type=str, help="search end date", location="args"
)
parser_search.add_argument(
    "size", type=str, help="Photo count per page", location="args"
)
parser_search.add_argument("page", type=str, help="Photo page", location="args")


parser_create = reqparse.RequestParser()
parser_create.add_argument("file", type=FileStorage, location="files")
parser_create.add_argument("action_ids", type=str, location="form", help="action ids")
parser_create.add_argument("pet_ids", type=str, location="form", help="pet ids")
parser_create.add_argument(
    "location_id", type=int, help="location ids", location="form"
)
parser_create.add_argument(
    "description", type=str, help="photo description", location="form"
)
parser_create.add_argument(
    "create_datetime", type=str, help="date of photo taken", location="form"
)


parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers")


@api.route("/")
class Photos(Resource, CustomeResponse):
    @api.doc(responses=set_doc_responses(200, 500))
    @api.expect(parser_search)
    @exception_handler
    def get(self):
        """List all photos"""
        args = parser_search.parse_args()
        return self.send(response_type="OK", result=get_photos(args))

    @api.doc(responses=set_doc_responses(202, 400, 401, 403, 500))
    @api.expect(parser_create, parser_auth)
    @login_required
    @exception_handler
    def post(self, **kwargs):
        """Upload a photo to Onedrive"""
        if kwargs["auth_user"].is_admin():
            args = parser_create.parse_args()
            if args.get("file") is None:
                return self.send(
                    response_type="BAD REQUEST", additional_message="No file to upload"
                )
            file = FileManager(args["file"])
            filename = file.save()

            args["filename"] = filename
            args["user_id"] = kwargs["auth_user"].id
            result, message = save_photo(args)
            if result:
                upload_files(filenames=[filename])
                return self.send(response_type="ACCEPTED", result=result.id)
            return self.send(response_type="BAD REQUEST", additional_message=message)

        return self.send(response_type="FORBIDDEN")


@api.route("/<id_>")
class Photo(Resource, CustomeResponse):
    @api.doc(responses=set_doc_responses(200, 404, 500))
    @api.doc("get_photo")
    @exception_handler
    def get(self, id_):
        """Get a photo by id"""
        if photo := PhotoModel.get_by_id(id_):
            return self.send(response_type="OK", result=photo.serialize)
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 400, 401, 403, 404, 500))
    @api.expect(parser_create, parser_auth)
    @login_required
    @exception_handler
    def put(self, id_, **kwargs):
        """Update photo info"""
        if PhotoModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                args = parser_create.parse_args()
                result, message = update_photo(id_, args)
                if result:
                    return self.send(response_type="NO CONTENT")
                return self.send(
                    response_type="BAD REQUEST", additional_message=message
                )
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 401, 403, 404, 500))
    @api.expect(parser_auth)
    @login_required
    @exception_handler
    def delete(self, id_, **kwargs):
        "Delete a photo by id"
        if PhotoModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                PhotoModel.delete_by_id(id_)
                return self.send(response_type="NO CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")
