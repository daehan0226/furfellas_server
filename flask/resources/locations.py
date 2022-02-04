import traceback
import sqlalchemy
from flask_restplus import Namespace, reqparse, Resource

from core.response import CustomeResponse
from core.models import Location as LocationModel
from core.database import db
from core.response import exception_handler, login_required

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
        return False, f"Location name '{name}' already exists."


def get_locations(name=None):
    if name is not None:
        locations = LocationModel.query.filter(LocationModel.name.like(f"%{name}%"))
    else:
        locations = LocationModel.query.all()
    return [location.serialize for location in locations]


def update_location(id_, name):
    location = LocationModel.query.get(id_)
    location.name = name
    db.session.commit()


parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers")


@api.route("/")
class Locations(Resource, CustomeResponse):
    @api.doc("Get all locations")
    @api.expect(parser_search)
    @exception_handler
    def get(self):
        args = parser_search.parse_args()
        return self.send(response_type="OK", result=get_locations(name=args["name"]))

    @api.doc("create a new location")
    @api.expect(parser_post, parser_auth)
    @login_required
    @exception_handler
    def post(self, **kwargs):
        if kwargs["auth_user"].is_admin():
            args = parser_post.parse_args()
            result, message = create_location(args["name"])
            if result:
                return self.send(response_type="CREATED", result=result.id)
            return self.send(response_type="BAD REQUEST", additional_message=message)

        return self.send(response_type="FORBIDDEN")


@api.route("/<int:id_>")
@api.param("id_", "The location identifier")
class Location(Resource, CustomeResponse):
    @exception_handler
    def get(self, id_):
        if location := LocationModel.get_by_id(id_):
            return self.send(response_type="OK", result=location.serialize)
        return self.send(response_type="NOT FOUND")

    @api.doc("update location name")
    @api.expect(parser_post, parser_auth)
    @login_required
    @exception_handler
    def put(self, id_, **kwargs):
        if LocationModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                args = parser_post.parse_args()
                update_location(id_, args["name"])
                return self.send(response_type="NO CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")

    @api.doc("delete a location")
    @api.expect(parser_auth)
    @login_required
    @exception_handler
    def delete(self, id_, **kwargs):
        if LocationModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                LocationModel.delete_by_id(id_)
                return self.send(response_type="NO CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")
