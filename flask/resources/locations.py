import traceback
from flask_restplus import Namespace, reqparse
from core.resource import CustomResource
from core import db

api = Namespace("locations", description="locations related operations")

parser_post = reqparse.RequestParser()
parser_post.add_argument("key", type=str, help="location key")
parser_post.add_argument("name", type=str, required=True, help="location name")


def get_locations():
    try:
        locations = db.get_locations()
        return locations
    except:
        traceback.print_exc()
        return None


def insert_location(name):
    try:
        result = db.insert_location(name)
        return result
    except:
        traceback.print_exc()
        return None


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
            result = insert_location(args["name"])
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
            result = db.update_location(id_, args["name"])
            if result is None:
                return self.send(status=500)
            return self.send(status=204)
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
