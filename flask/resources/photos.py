import traceback
import werkzeug
import os
import sqlalchemy
from datetime import datetime
from flask_restplus import Namespace, reqparse, Resource
from werkzeug.datastructures import FileStorage
from apiclient.http import MediaFileUpload

from core.database import db
from core.models import Photo as PhotoModel, Action as ActionModel
from core.google_drive_api import get_service, get_folder_id
from core.response import (
    CustomeResponse,
    return_500_for_sever_error,
    return_401_for_no_auth,
)


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
        return False, "Wrong location id"
    except sqlalchemy.orm.exc.FlushError as e:
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
    PhotoModel.query.filter_by(id=id).delete()


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


parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers")


@api.route("/")
class Photos(Resource, CustomeResponse):
    @api.doc("list_photos")
    @api.expect(parser_search)
    @return_500_for_sever_error
    def get(self):
        """List all photos"""
        args = parser_search.parse_args()
        return self.send(response_type="SUCCESS", result=get_photos(args))

    @api.doc("post a photo")
    @api.expect(parser_create, parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def post(self, **kwargs):
        """Upload a photo to Onedrive"""
        if kwargs["auth_user"].is_admin():
            args = parser_create.parse_args()
            if image_id := upload_photo(args["file"]):
                args["image_id"] = image_id
                args["create_datetime"] = datetime.now()
                args["user_id"] = kwargs["auth_user"].id
                result, message = save_photo(args)
                if result:
                    return self.send(response_type="CREATED", result=result.id)
                return self.send(response_type="FAIL", additional_message=message)
        return self.send(response_type="FORBIDDEN")


@api.route("/<id_>")
class Photo(Resource, CustomeResponse):
    @api.doc("get_photo")
    @return_500_for_sever_error
    def get(self, id_):
        if photo := get_photo(id_):
            return self.send(response_type="SUCCESS", result=photo)
        return self.send(response_type="NOT_FOUND")

    @api.doc("delete a photo")
    @api.expect(parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def delete(self, id_, **kwargs):
        if get_photo(id_):
            if kwargs["auth_user"].is_admin():
                delete_photo(id_)
                return self.send(response_type="NO_CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")
