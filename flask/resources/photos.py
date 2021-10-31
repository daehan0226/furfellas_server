import traceback
import werkzeug
import os
import sqlalchemy
from datetime import datetime
from flask_restplus import Namespace, reqparse
from werkzeug.datastructures import FileStorage
from apiclient.http import MediaFileUpload

from core.database import db
from core.models import Photo as PhotoModel, Action as ActionModel
from core.google_drive_api import get_service, get_folder_id
from core.resource import CustomResource


api = Namespace("photos", description="Photos related operations")


def upload_photo(file):
    image_id = None
    filename = werkzeug.secure_filename(file.filename)
    file_dir = f"tmp\{filename}"
    folder_id = get_folder_id()
    file_metadata = {
        "name": filename,
        "parents": [folder_id],
    }
    file.save(file_dir)
    media = MediaFileUpload(file_dir, mimetype=file.content_type, resumable=True)
    service = get_service()
    result = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    image_id = result["id"]
    return image_id


def save_photo(photo_columns):
    try:
        photo = PhotoModel(**photo_columns)
        action_ids = photo_columns["action_ids"].split(",")
        photo.actions = [
            ActionModel.query.get(int(action_id)) for action_id in action_ids
        ]
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


def get_photos(args):
    try:
        query = db.session.query(PhotoModel)
        if args["type_ids"] is not None:
            type_ids = (int(type_id) for type_id in args["type_ids"].split(","))
            query = query.filter(PhotoModel.type_id.in_(type_ids))
        if args["location_ids"] is not None:
            location_ids = (
                int(location_id) for location_id in args["location_ids"].split(",")
            )
            query = query.filter(PhotoModel.location_id.in_(location_ids))
        if args["action_ids"] is not None:
            action_ids = (int(action_id) for action_id in args["action_ids"].split(","))
            query = query.join(PhotoModel.actions).filter(
                ActionModel.id.in_(action_ids)
            )
        photos = query.all()
        return [photo.serialize for photo in photos]
    except:
        traceback.print_exc()
        return False


def get_photo(id):
    photo = PhotoModel.query.get(id)
    if photo:
        photo = photo.serialize
        print(photo)
        return photo
    return None


def delete_photo(id):
    return PhotoModel.query.filter_by(id=id).delete()


parser_search = reqparse.RequestParser()
parser_search.add_argument(
    "type_ids", type=str, location="args", help="Alone or together"
)
parser_search.add_argument(
    "action_ids", type=str, location="args", help="action ids or new actions"
)
parser_search.add_argument(
    "location_ids", type=str, help="location ids or new locations", location="args"
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
parser_create.add_argument("file", type=FileStorage, location="files", required=True)
parser_create.add_argument(
    "type_id", type=int, location="form", help="Alone or together"
)
parser_create.add_argument(
    "action_ids", type=str, location="form", help="action ids or new actions"
)
parser_create.add_argument(
    "location_id", type=int, help="location ids or new locations", location="form"
)
parser_create.add_argument(
    "description", type=str, help="photo description", location="form"
)
parser_create.add_argument(
    "create_datetime", type=str, help="date of photo taken", location="form"
)


@api.route("/")
class Photos(CustomResource):
    @api.doc("list_photos")
    @api.expect(parser_search)
    def get(self):
        """List all photos"""
        try:
            args = parser_search.parse_args()
            photos = get_photos(args)
            return self.send(status=200, result=photos)

        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("post a photo")
    @api.expect(parser_create)
    def post(self):
        """Upload a photo to Onedrive"""
        try:
            args = parser_create.parse_args()
            image_id = upload_photo(args["file"])
            if image_id:
                args["image_id"] = image_id
                args["create_datetime"] = datetime.now()
                result, message = save_photo(args)
                if result:
                    return self.send(status=201, result=result.id)
                else:
                    return self.send(status=400, message=message)
            return self.send(status=400)
        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/<id_>")
@api.response(404, "photo not found")
class Photo(CustomResource):
    @api.doc("get_photo")
    def get(self, id_):
        try:
            photo = get_photo(id_)
            if photo:
                return self.send(status=200, result=photo)
            return self.send(status=404)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("delete a photo")
    def delete(self, id_):
        try:
            result = delete_photo(id_)
            if result is None:
                return self.send(status=500)
            return self.send(status=200)
        except:
            traceback.print_exc()
            return self.send(status=500)
