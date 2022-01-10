import traceback
import sqlalchemy
from dateutil.relativedelta import relativedelta
from flask_restplus import Namespace, reqparse, Resource
from sqlalchemy import exc
from werkzeug.datastructures import FileStorage

from core.database import db
from core.models import Photo as PhotoModel, Action as ActionModel, Pet as PetModel
from core.google_drive_api import GoogleManager
from core.response import (
    CustomeResponse,
    return_500_for_sever_error,
    return_401_for_no_auth,
)
from core.utils import convert_to_datetime, convert_str_ids_to_int_ids_tuple
from core.file_manager import FileManager
from core.errors import FileSaveError


api = Namespace("photos", description="Photos related operations")


def save_file(file):
    try:
        file = FileManager(file)
        file.save()
        return file.name
    except:
        traceback.print_exc()
        raise FileSaveError


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
        return False, "Something went wrong"
        # return photo.create(), ""
    except sqlalchemy.exc.IntegrityError as e:
        return False, "Wrong location id"
    except sqlalchemy.orm.exc.FlushError as e:
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
            if args.get("file") is None:
                return self.send(
                    response_type="FAIL", additional_message="No file to upload"
                )
            # google_service = GoogleManager.instance()
            # if image_id := google_service.upload_photo(args["file"]):
            # args["image_id"] = image_id
            args["user_id"] = kwargs["auth_user"].id
            args["file_name"] = save_file(args["file"])

            result, message = save_photo(args)
            if result:
                return self.send(response_type="ACCEPTED", result=result.id)
            return self.send(response_type="FAIL", additional_message=message)

        return self.send(response_type="FORBIDDEN")


@api.route("/<id_>")
class Photo(Resource, CustomeResponse):
    @api.doc("get_photo")
    @return_500_for_sever_error
    def get(self, id_):
        if photo := PhotoModel.get_by_id(id_):
            return self.send(response_type="SUCCESS", result=photo.serialize)
        return self.send(response_type="NOT_FOUND")

    @api.doc("update a photo")
    @api.expect(parser_create, parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def put(self, id_, **kwargs):
        """Upload a photo to Onedrive"""
        if PhotoModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                args = parser_create.parse_args()
                result, message = update_photo(id_, args)
                if result:
                    return self.send(response_type="NO_CONTENT")
                return self.send(response_type="FAIL", additional_message=message)
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")

    @api.doc("delete a photo")
    @api.expect(parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def delete(self, id_, **kwargs):
        if PhotoModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                PhotoModel.delete_by_id(id_)
                return self.send(response_type="NO_CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")
