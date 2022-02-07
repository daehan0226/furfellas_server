from flask_restplus import Namespace, reqparse, Resource
from app.core.response import (
    CustomeResponse,
    exception_handler,
    login_required,
)
from app.core.models import UserRole
from app.core.utils import set_doc_responses

api = Namespace("user-roles", description="User role related operations")

parser_post = reqparse.RequestParser()
parser_post.add_argument("name", type=str, help="user_role name")
parser_post.add_argument("description", type=str, help="user_role description")


parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers")


@api.route("/")
class UserRoles(Resource, CustomeResponse):
    @api.doc(responses=set_doc_responses(200, 500))
    @exception_handler
    def get(self):
        """Get all user roles."""
        return self.send(response_type="OK", result=UserRole.get_user_roles())

    @api.doc(responses=set_doc_responses(201, 400, 403, 500))
    @api.expect(parser_post, parser_auth)
    @login_required
    @exception_handler
    def post(self, **kwargs):
        """create a new user role"""
        if kwargs["auth_user"].is_admin():
            args = parser_post.parse_args()
            result, message = UserRole.create_user_role(
                args["name"], args.get("description") or ""
            )
            if result:
                return self.send(response_type="CREATED", result=result.id)
            return self.send(response_type="BAD REQUEST", additional_message=message)
        return self.send(response_type="FORBIDDEN")


@api.route("/<int:id_>")
class user_role(Resource, CustomeResponse):
    @api.doc(
        params={"id_": "The user role identifier"},
        responses=set_doc_responses(200, 404, 500),
    )
    @exception_handler
    def get(self, id_):
        """Get user role by id."""
        if user_role := UserRole.get_by_id(id_):
            return self.send(response_type="OK", result=user_role.serialize)
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 401, 403, 404, 409, 500))
    @api.expect(parser_post, parser_auth)
    @login_required
    @exception_handler
    def put(self, id_, **kwargs):
        """Update the name of the user role."""
        if UserRole.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                args = parser_post.parse_args()
                if UserRole.get_by_name(args["name"]):
                    return self.send(
                        response_type="CONFLICT",
                        additional_message=f"{args['name']} already exists ",
                    )
                UserRole.update_user_role(id_, args["name"])
                return self.send(response_type="NO CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 401, 403, 404, 500))
    @api.expect(parser_auth)
    @login_required
    @exception_handler
    def delete(self, id_, **kwargs):
        """Delete the user role."""
        if UserRole.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                UserRole.delete_by_id(id_)
                return self.send(response_type="NO CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")
