import traceback
from flask_restplus import Namespace, reqparse
from core.resource import CustomResource
from core.models import Location as LocationModel
from core.database import db

api = Namespace("locations", description="locations related operations")

parser_post = reqparse.RequestParser()
parser_post.add_argument("key", type=str, help="location key")
parser_post.add_argument("name", type=str, required=True, help="location name")


def create_location(name):
    location = LocationModel(name)
    location.create()
    return location.id


def get_location(id):
    location = LocationModel.query.filter_by(id=id).first()
    return location.serialize if location else None


def update_location(id, name):
    try:
        location = LocationModel.query.filter_by(id=id).first()
        location.name = name
        db.session.commit()
        return True
    except:
        return False


def delete_location(id):
    return LocationModel.query.filter_by(id=id).delete()


def get_locations():
    return [location.serialize for location in LocationModel.query.all()]


@api.route("/")
class Locations(CustomResource):
    @api.doc("Get all locations")
    def get(self):
        try:
            locations = get_locations()
            if locations is None:
                return self.send(status=500)
            return self.send(status=200, result=locations)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("create a new location")
    @api.expect(parser_post)
    def post(self):
        try:
            args = parser_post.parse_args()
            result = create_location(args["name"])
            if result is None:
                return self.send(status=500)
            return self.send(status=201)

        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/<int:id_>")
@api.param("id_", "The location identifier")
class Location(CustomResource):
    @api.doc("update location name")
    @api.expect(parser_post)
    def put(self, id_):
        try:
            args = parser_post.parse_args()
            result = update_location(id_, args["name"])
            if result:
                return self.send(status=204)
            return self.send(status=400)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("delete a location")
    def delete(self, id_):
        try:
            result = db.delete_location(id_)
            if result is None:
                return self.send(status=500)
            return self.send(status=200)

        except:
            traceback.print_exc()
            return self.send(status=500)
