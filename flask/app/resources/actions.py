from flask_restplus import Namespace, reqparse, Resource

from app.core.response import (
    CustomeResponse,
    exception_handler,
    login_required,
)
from app.core.models import Action as ActionModel
from app.core.utils import set_doc_responses

api = Namespace("actions", description="Actions related operations")

parser_post = reqparse.RequestParser()
parser_post.add_argument(
    "name", type=str, required=True, help="New action name", location="json"
)

parser_search = reqparse.RequestParser()
parser_search.add_argument(
    "name", type=str, help="Find actions that includes the given name"
)

parser_auth = reqparse.RequestParser()
parser_auth.add_argument(
    "Authorization",
    type=str,
    location="headers",
    help="Session token",
)


@api.route("/")
class Actions(Resource, CustomeResponse):
    @api.doc(responses=set_doc_responses(200, 500))
    @api.expect(parser_search)
    @exception_handler
    def get(self):
        """Get all actions with filter by name if given."""
        args = parser_search.parse_args()
        return self.send(
            response_type="OK", result=ActionModel.get_all(name=args["name"])
        )

    @api.doc(responses=set_doc_responses(201, 401, 403, 409, 500))
    @api.expect(parser_post, parser_auth)
    @login_required
    @exception_handler
    def post(self, **kwargs):
        """Create a new action."""
        if kwargs["auth_user"].is_admin():
            args = parser_post.parse_args()
            result, message = ActionModel.create(args["name"])
            if result:
                return self.send(response_type="CREATED", result=result.id)
            return self.send(response_type="CONFLICT", additional_message=message)
        return self.send(response_type="FORBIDDEN")


@api.doc(params={"id_": "The action identifier"})
@api.route("/<int:id_>")
class Action(Resource, CustomeResponse):
    @api.doc(responses=set_doc_responses(200, 404, 500))
    @exception_handler
    def get(self, id_):
        """Get action by id value."""
        if action := ActionModel.get_by_id(id_):
            return self.send(response_type="OK", result=action.serialize)
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 401, 403, 404, 409, 500))
    @api.expect(parser_post, parser_auth)
    @login_required
    @exception_handler
    def put(self, id_, **kwargs):
        """Update the name of the action."""
        if action := ActionModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                args = parser_post.parse_args()
                if action.name == args["name"]:
                    return self.send(response_type="NO CONTENT")
                if ActionModel.get_by_name(args["name"]):
                    return self.send(
                        response_type="CONFLICT",
                        additional_message=f"{args['name']} already exists ",
                    )
                ActionModel.update(id_, args["name"])
                return self.send(response_type="NO CONTENT")

            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 401, 403, 404, 500))
    @api.expect(parser_auth)
    @login_required
    @exception_handler
    def delete(self, id_, **kwargs):
        """Delete the action."""
        if ActionModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                ActionModel.delete_by_id(id_)
                return self.send(response_type="NO CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")
