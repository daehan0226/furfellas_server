import traceback
import sqlalchemy
from flask_restplus import Namespace, reqparse
from core.resource import CustomResource
from core.models import Location as LocationModel
from core.database import db
from core.constants import response_status

api = Namespace("locations", description="locations related operations")

parser_post = reqparse.RequestParser()
parser_post.add_argument("key", type=str, help="location key")
parser_post.add_argument("name", type=str, required=True, help="location name")

parser_search = reqparse.RequestParser()
parser_search.add_argument("name", type=str, help="location name")


def create_location(name):
    try:
        location = LocationModel(name)
        location.create()
        return location, ""
    except sqlalchemy.exc.IntegrityError as e:
        return False, f"Location name '{name}' already exsits."


def get_locations(name=None):
    if name is not None:
        locations = LocationModel.query.filter(LocationModel.name.like(f"%{name}%"))
    else:
        locations = LocationModel.query.all()
    return [location.serialize for location in locations]


def get_location(id_):
    location = LocationModel.query.get(id_)
    return location.serialize if location else None


def update_location(id_, name):
    location = LocationModel.query.get(id_)
    location.name = name
    db.session.commit()


def delete_location(id_):
    LocationModel.query.filter_by(id=id_).delete()


@api.route("/")
class Locations(CustomResource):
    @api.doc("Get all locations")
    def get(self):
        try:
            args = parser_search.parse_args()
            return self.send(
                status=response_status.SUCCESS, result=get_locations(name=args["name"])
            )
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    @api.doc("create a new location")
    @api.expect(parser_post)
    def post(self):
        try:
            args = parser_post.parse_args()
            result, message = create_location(args["name"])
            if result:
                return self.send(status=response_status.CREATED, result=result.id)
            return self.send(status=response_status.FAIL, message=message)

        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)


@api.route("/<int:id_>")
@api.param("id_", "The location identifier")
class Location(CustomResource):
    def get(self, id_):
        try:
            location = get_location(id_)
            if location:
                return self.send(status=response_status.SUCCESS, result=location)
            return self.send(status=response_status.NOT_FOUND)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    @api.doc("update location name")
    @api.expect(parser_post)
    def put(self, id_):
        try:
            if update_location(id_):
                args = parser_post.parse_args()
                update_location(id_, args["name"])
                return self.send(status=response_status.NO_CONTENT)
            return self.send(status=response_status.NOT_FOUND)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    @api.doc("delete a location")
    def delete(self, id_):
        try:
            if get_location(id_):
                delete_location(id_)
                return self.send(status=response_status.NO_CONTENT)
            return self.send(status=response_status.NOT_FOUND)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)
