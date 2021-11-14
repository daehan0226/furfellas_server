import traceback
import sqlalchemy
from flask_restplus import Namespace, reqparse, Resource

from core.response import CustomeResponse
from core.models import PhotoType as PhotoTypeModel
from core.database import db
from core.response import return_500_for_sever_error, return_401_for_no_auth

api = Namespace("photo-types", description="photo types related operations")

parser_name = reqparse.RequestParser()
parser_name.add_argument("name", type=str, required=True, help="photo type name")


def create_photo_type(name):
    try:
        photo_type = PhotoTypeModel(name)
        photo_type.create()
        return photo_type, ""
    except sqlalchemy.exc.IntegrityError as e:
        return False, f"Photo type '{name}' already exsits."


def get_photo_type(id):
    photo_type = PhotoTypeModel.query.filter_by(id=id).first()
    return photo_type.serialize if photo_type else None


def update_photo_type(id, name):
    photo_type = PhotoTypeModel.query.filter_by(id=id).first()
    photo_type.name = name
    db.session.commit()


def delete_photo_type(id):
    PhotoTypeModel.query.filter_by(id=id).delete()
    db.session.commit()


def get_photo_types():
    return [photo_type.serialize for photo_type in PhotoTypeModel.query.all()]


parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers")


@api.route("/")
class PhotoTypes(Resource, CustomeResponse):
    @return_500_for_sever_error
    def get(self):
        return self.send(response_type="SUCCESS", result=get_photo_types())

    @api.expect(parser_name, parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def post(self, **kwargs):
        if kwargs["auth_user"].is_admin():
            args = parser_name.parse_args()
            result, message = create_photo_type(args["name"])
            if result:
                return self.send(response_type="CREATED", result=result.id)
            return self.send(response_type="FAIL", additional_message=message)
        return self.send(response_type="FORBIDDEN")


@api.route("/<int:id_>")
@api.param("id_", "The photo type identifier")
class PhotoType(Resource, CustomeResponse):
    @return_500_for_sever_error
    def get(self, id_):
        if photo_type := get_photo_type(id_):
            return self.send(response_type="SUCCESS", result=photo_type)
        return self.send(response_type="NOT_FOUND")

    @api.expect(parser_name, parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def put(self, id_, **kwargs):
        if get_photo_type(id_):
            if kwargs["auth_user"].is_admin():
                args = parser_name.parse_args()
                update_photo_type(id_, args["name"])
                return self.send(response_type="NO_CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")

    @api.expect(parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def delete(self, id_, **kwargs):
        if kwargs["auth_user"].is_admin():
            if get_photo_type(id_):
                delete_photo_type(id_)
                return self.send(response_type="NO_CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")
