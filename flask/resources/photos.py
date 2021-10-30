import traceback
import werkzeug
import os
import sqlalchemy
from datetime import datetime
from flask_restplus import Namespace, reqparse
from werkzeug.datastructures import FileStorage
from apiclient.http import MediaFileUpload

from core.models import Photo as PhotoModel, Action as ActionModel
from core.google_drive_api import get_service, get_folder_id
from core.resource import CustomResource, json_serializer
from core.db import (
    search_photos,
    get_photo_actions,
    delete_photo,
    verify_photo_actions,
)

api = Namespace("photos", description="Photos related operations")

photo_types = [
    {"id": 0, "name": "Together"},
    {"id": 1, "name": "Aibi"},
    {"id": 2, "name": "Sevi"},
]


def filter_photos_by_actions(photos, actions):
    filtered = []

    for photo in photos:
        photo_action = verify_photo_actions(photo["id"], actions)
        if photo_action:
            filtered.append(photo)

    return filtered


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
        types = []
        locations = []
        if args["types"]:
            types = args["types"].split(",")

        if args["locations"]:
            locations = args["locations"].split(",")

        photos = search_photos(
            types, locations, args["start_datetime"], args["end_datetime"]
        )

        if args["actions"]:
            actions = args["actions"].split(",")
            photos = filter_photos_by_actions(photos, actions)

        for photo in photos:
            photo["datetime"] = json_serializer(photo["datetime"])
            photo["upload_datetime"] = json_serializer(photo["upload_datetime"])
            photo["actions"] = get_photo_actions(photo["id"])
            photo["type"] = photo_types[photo["type"]]
            photo["location"] = {
                "id": photo["location_id"],
                "name": photo["location_name"],
            }
            del photo["location_id"]
            del photo["location_name"]

        return photos
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


parser_search = reqparse.RequestParser()
parser_search.add_argument("types", type=str, location="args", help="Alone or together")
parser_search.add_argument(
    "actions", type=str, location="args", help="action ids or new actions"
)
parser_search.add_argument(
    "locations", type=str, help="location ids or new locations", location="args"
)
parser_search.add_argument(
    "start_datetime", type=str, help="search start date", location="args"
)
parser_search.add_argument(
    "end_datetime", type=str, help="search end date", location="args"
)
parser_search.add_argument("size", type=str, help="Photo count", location="args")

parser_create = reqparse.RequestParser()
parser_create.add_argument("file", type=FileStorage, location="files", required=True)
parser_create.add_argument("type", type=int, location="form", help="Alone or together")
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
    "date", type=str, help="date of photo taken", location="form"
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
            print(photo)
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


@api.route("/types")
class PhotoTypes(CustomResource):
    @api.doc("list_types")
    def get(self):
        try:
            global photo_types
            return self.send(status=200, result=photo_types)

        except:
            traceback.print_exc()
            return self.send(status=500)
