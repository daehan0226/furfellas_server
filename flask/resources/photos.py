from flask_restplus import Namespace, reqparse, Resource
from werkzeug.datastructures import FileStorage

from core.models import Photo as PhotoModel
from core.response import (
    CustomeResponse,
    exception_handler,
    login_required,
)
from core.file_manager import FileManager
from core.utils import set_doc_responses

api = Namespace("photos", description="Photos related operations")


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
        return self.send(response_type="OK", result=PhotoModel.get_photos(args))

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
            result, message = PhotoModel.save_photo(args)
            if result:
                PhotoModel.upload_files(filenames=[filename])
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
                result, message = PhotoModel.update_photo(id_, args)
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
