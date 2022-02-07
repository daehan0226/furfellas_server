from flask_restplus import Namespace, reqparse, Resource
from app.core.response import (
    exception_handler,
    login_required,
    gen_dupilcate_keys_message,
    CustomeResponse,
)
from app.core.models import User as UserModel
from app.core.models import UserProfile as UserProfileModel
from app.core.utils import set_doc_responses


api = Namespace("users", description="Users related operations")


parser_create = reqparse.RequestParser()
parser_create.add_argument("username", type=str, required=True, help="Unique user name")
parser_create.add_argument("email", type=str)
parser_create.add_argument("password", type=str, required=True, help="Password")

parser_delete = reqparse.RequestParser()
parser_delete.add_argument("ids", type=str, required=True, action="split")

parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers")

parser_search = reqparse.RequestParser()
parser_search.add_argument("username", type=str, help="Unique user name")
parser_search.add_argument("email", type=str)


@api.route("/")
class Users(Resource, CustomeResponse):
    @api.doc(responses=set_doc_responses(200, 401, 403, 500))
    @api.expect(parser_search, parser_auth)
    @login_required
    @exception_handler
    def get(self, **kwargs):
        """Get all users"""
        if kwargs["auth_user"].is_admin():
            args = parser_search.parse_args()
            return self.send(
                response_type="OK", result=UserProfileModel.get_users(args)
            )
        return self.send(response_type="FORBIDDEN")

    @api.doc(responses=set_doc_responses(201, 400, 409, 500))
    @api.expect(parser_create)
    @exception_handler
    def post(self):
        """Create an user"""
        args = parser_create.parse_args()
        if duplicate_keys := UserProfileModel.check_user_info_duplicates(args):
            return self.send(
                response_type="CONFLICT",
                additional_message=gen_dupilcate_keys_message(duplicate_keys),
            )
        result = UserModel.create_user(args)
        return self.send(response_type="CREATED", result=result.id)


@api.route("/<int:id_>")
class User(Resource, CustomeResponse):
    @api.doc(
        params={"id_": "The user identifier"},
        responses=set_doc_responses(200, 401, 404, 500),
    )
    @api.expect(parser_auth)
    @login_required
    @exception_handler
    def get(self, id_, **kwargs):
        """Get user by id."""
        if user := UserModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin() or kwargs["auth_user"].id == id_:
                return self.send(response_type="OK", result=user.serialize)
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 401, 403, 404, 500))
    @api.expect(parser_auth)
    @login_required
    @exception_handler
    def delete(self, id_, **kwargs):
        """Delete the user."""
        if UserModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                UserModel.delete_by_id(id_)
                return self.send(response_type="NO CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 401, 403, 404, 500))
    @api.expect(parser_create, parser_auth)
    @login_required
    @exception_handler
    def put(self, id_, **kwargs):
        """Update the user info."""
        if UserModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                args = parser_create.parse_args()
                UserProfileModel.update_user(UserModel.query.get(id_), args)
                return self.send(response_type="NO CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")
