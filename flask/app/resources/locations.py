from flask_restplus import Namespace, reqparse, Resource

from app.core.response import CustomeResponse
from app.core.models import Location as LocationModel
from app.core.response import exception_handler, login_required
from app.core.utils import set_doc_responses

api = Namespace("locations", description="Locations related operations")

parser_post = reqparse.RequestParser()
parser_post.add_argument(
    "name", type=str, required=True, location="json", help="New location name"
)

parser_search = reqparse.RequestParser()
parser_search.add_argument("name", type=str, help="Location name")

parser_auth = reqparse.RequestParser()
parser_auth.add_argument(
    "Authorization", type=str, location="headers", help="Session token"
)


@api.route("/")
class Locations(Resource, CustomeResponse):
    @api.doc(responses=set_doc_responses(200, 500))
    @api.expect(parser_search)
    @exception_handler
    def get(self):
        """Get all locations with filter by name if given."""
        args = parser_search.parse_args()
        return self.send(
            response_type="OK", result=LocationModel.get_all(name=args["name"])
        )

    @api.doc(responses=set_doc_responses(201, 401, 403, 409, 500))
    @api.expect(parser_post, parser_auth)
    @login_required
    @exception_handler
    def post(self, **kwargs):
        """Create a new location."""
        if kwargs["auth_user"].is_admin():
            args = parser_post.parse_args()
            result, message = LocationModel.create(args["name"])
            if result:
                return self.send(response_type="CREATED", result=result.id)
            return self.send(response_type="CONFLICT", additional_message=message)

        return self.send(response_type="FORBIDDEN")


@api.doc(params={"id_": "The location identifier"})
@api.route("/<int:id_>")
class Location(Resource, CustomeResponse):
    @api.doc(
        responses=set_doc_responses(200, 404, 500),
    )
    @exception_handler
    def get(self, id_):
        """Get location by id value."""
        if location := LocationModel.get_by_id(id_):
            return self.send(response_type="OK", result=location.serialize)
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 401, 403, 404, 409, 500))
    @api.expect(parser_post, parser_auth)
    @login_required
    @exception_handler
    def put(self, id_, **kwargs):
        """Update the name of the location."""
        if location := LocationModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                args = parser_post.parse_args()
                if location.name == args["name"]:
                    return self.send(response_type="NO CONTENT")
                if LocationModel.get_by_name(args["name"]):
                    return self.send(
                        response_type="CONFLICT",
                        additional_message=f"{args['name']} already exists ",
                    )
                LocationModel.update(id_, args["name"])
                return self.send(response_type="NO CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 401, 403, 404, 500))
    @api.expect(parser_auth)
    @login_required
    @exception_handler
    def delete(self, id_, **kwargs):
        """Delete the location."""
        if LocationModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                LocationModel.delete_by_id(id_)
                return self.send(response_type="NO CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")
