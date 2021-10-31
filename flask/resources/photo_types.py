import traceback
from flask_restplus import Namespace, reqparse

from core.resource import CustomResource
from core.models import PhotoType as PhotoTypeModel
from core.database import db

api = Namespace("photo-types", description="photo types related operations")

parser_post = reqparse.RequestParser()
parser_post.add_argument("name", type=str, required=True, help="photo type name")


def create_photo_type(name):
    photo_type = PhotoTypeModel(name)
    photo_type.create()
    return photo_type.id


def get_photo_type(id):
    photo_type = PhotoTypeModel.query.filter_by(id=id).first()
    return photo_type.serialize if photo_type else None


def update_photo_type(id, name):
    try:
        photo_type = PhotoTypeModel.query.filter_by(id=id).first()
        photo_type.name = name
        db.session.commit()
        return True
    except:
        return False


def delete_photo_type(id):
    return PhotoTypeModel.query.filter_by(id=id).delete()


def get_photo_types():
    return [photo_type.serialize for photo_type in PhotoTypeModel.query.all()]


@api.route("/")
class PhotoTypes(CustomResource):
    def get(self):
        try:
            return self.send(status=200, result=get_photo_types())
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.expect(parser_post)
    def post(self):
        try:
            args = parser_post.parse_args()
            result = create_photo_type(args["name"])
            if result is None:
                return self.send(status=500)
            return self.send(status=201)
        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/<int:id_>")
@api.param("id_", "The photo type identifier")
class PhotoType(CustomResource):
    @api.expect(parser_post)
    def put(self, id_):
        try:
            args = parser_post.parse_args()
            result = update_photo_type(id_, args["name"])
            return self.send(status=204) if result else self.send(status=400)
        except:
            traceback.print_exc()
            return self.send(status=500)

    def delete(self, id_):
        try:
            result = delete_photo_type(id_)
            if result is None:
                return self.send(status=500)
            return self.send(status=200)

        except:
            traceback.print_exc()
            return self.send(status=500)
