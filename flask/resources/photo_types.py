import traceback
import sqlalchemy
from flask_restplus import Namespace, reqparse

from core.constants import response_status
from core.resource import CustomResource
from core.models import PhotoType as PhotoTypeModel
from core.database import db

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


def get_photo_types():
    return [photo_type.serialize for photo_type in PhotoTypeModel.query.all()]


@api.route("/")
class PhotoTypes(CustomResource):
    def get(self):
        try:
            return self.send(status=response_status.SUCCESS, result=get_photo_types())
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    @api.expect(parser_name)
    def post(self):
        try:
            args = parser_name.parse_args()
            result, message = create_photo_type(args["name"])
            if result:
                return self.send(status=response_status.CREATED, result=result.id)
            return self.send(status=response_status.FAIL, message=message)

        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)


@api.route("/<int:id_>")
@api.param("id_", "The photo type identifier")
class PhotoType(CustomResource):
    def get(self, id_):
        try:
            photo_type = get_photo_type(id_)
            if photo_type:
                return self.send(status=response_status.SUCCESS, result=photo_type)
            return self.send(status=response_status.NOT_FOUND)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    @api.expect(parser_name)
    def put(self, id_):
        try:
            if get_photo_type(id_):
                args = parser_name.parse_args()
                update_photo_type(id_, args["name"])
                return self.send(status=response_status.NO_CONTENT)
            return self.send(status=response_status.NOT_FOUND)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    def delete(self, id_):
        try:
            if get_photo_type(id_):
                delete_photo_type(id_)
                return self.send(status=response_status.NO_CONTENT)
            return self.send(status=response_status.NOT_FOUND)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)
