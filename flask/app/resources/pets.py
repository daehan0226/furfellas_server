from flask_restplus import Namespace, reqparse, Resource

from app.core.response import (
    CustomeResponse,
    exception_handler,
    login_required,
)
from app.core.models import Pet as PetModel
from app.core.utils import set_doc_responses

api = Namespace("pets", description="Pets related operations")

parser_post = reqparse.RequestParser()
parser_post.add_argument("name", type=str, required=True)
parser_post.add_argument("weight", type=int, required=True)
parser_post.add_argument("birthday", type=str, required=True)
parser_post.add_argument("color", type=str, help="CSS HEX", required=True)
parser_post.add_argument("intro", type=str, required=True)
parser_post.add_argument("photo_id", type=str)

parser_search = reqparse.RequestParser()
parser_search.add_argument("name", type=str, help="pet name")

parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers")


@api.route("/")
class Pets(Resource, CustomeResponse):
    @api.doc(responses=set_doc_responses(200, 500))
    @api.expect(parser_search)
    @exception_handler
    def get(self):
        """Get all pets with filter by name if given."""
        args = parser_search.parse_args()
        result = None
        if args.get("name") is None:
            result = PetModel.get_pets()
        else:
            result = PetModel.get_by_name(args["name"])

        return self.send(response_type="OK", result=result)

    @api.doc(responses=set_doc_responses(201, 401, 403, 409, 500))
    @api.expect(parser_post, parser_auth)
    @login_required
    @exception_handler
    def post(self, **kwargs):
        """Create a new pet."""
        if kwargs["auth_user"].is_admin():
            args = parser_post.parse_args()
            result, message = PetModel.create(args)
            if result:
                return self.send(response_type="CREATED", result=result.id)
            return self.send(response_type="BAD REQUEST", additional_message=message)
        return self.send(response_type="FORBIDDEN")


@api.route("/<int:id_>")
class Pet(Resource, CustomeResponse):
    @api.doc(
        params={"id_": "The pet identifier"},
        responses=set_doc_responses(200, 404, 500),
    )
    @exception_handler
    def get(self, id_):
        if pet := PetModel.get_by_id(id_):
            return self.send(response_type="OK", result=pet.serialize)
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 401, 403, 404, 409, 500))
    @api.expect(parser_post, parser_auth)
    @login_required
    @exception_handler
    def put(self, id_, **kwargs):
        """Update the name of the pet."""
        if PetModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                args = parser_post.parse_args()
                if PetModel.get_by_name(args["name"]):
                    return self.send(
                        response_type="CONFLICT",
                        additional_message=f"{args['name']} already exists ",
                    )
                PetModel.update_name(id_, args["name"])
                return self.send(response_type="NO CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 401, 403, 404, 500))
    @api.expect(parser_auth)
    @login_required
    @exception_handler
    def delete(self, id_, **kwargs):
        """Delete the pet."""
        if PetModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                PetModel.delete_by_id(id_)
                return self.send(response_type="NO CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")
