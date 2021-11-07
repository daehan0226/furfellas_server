import sqlalchemy
from flask_restplus import Namespace, reqparse, Resource
from core.response import (
    CustomeResponse,
    return_500_for_sever_error,
    return_401_for_no_auth,
)
from core.models import UserRole
from core.database import db

api = Namespace("user-roles", description="User role related operations")

parser_post = reqparse.RequestParser()
parser_post.add_argument("name", type=str, help="user_role name")
parser_post.add_argument("description", type=str, help="user_role description")


def create_user_role(name, description):
    try:
        user_role = UserRole(name, description)
        user_role.create()
        return user_role, ""
    except sqlalchemy.exc.IntegrityError as e:
        return False, f"User_role name '{name}' already exsits."


def get_user_roles():
    return [user_role.serialize for user_role in UserRole.query.all()]


def get_user_role(id_):
    user_role = UserRole.query.get(id_)
    return user_role.serialize if user_role else None


def update_user_role(id_, name):
    user_role = UserRole.query.get(id_)
    user_role.name = name
    db.session.commit()


def delete_user_role(id_):
    UserRole.query.filter_by(id=id_).delete()


parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers")


@api.route("/")
class UserRoles(Resource, CustomeResponse):
    @api.doc("Get all user_roles")
    @return_500_for_sever_error
    def get(self):
        return self.send(response_type="SUCCESS", result=get_user_roles())

    @api.doc("create a new user_role")
    @api.expect(parser_post, parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def post(self, **kwargs):
        if kwargs["auth_user"].is_admin():
            args = parser_post.parse_args()
            result, message = create_user_role(
                args["name"], args.get("description") or ""
            )
            if result:
                return self.send(response_type="CREATED", result=result.id)
            return self.send(response_type="FAIL", additional_message=message)
        return self.send(response_type="FORBIDDEN")


@api.route("/<int:id_>")
@api.param("id_", "The user_role identifier")
class user_role(Resource, CustomeResponse):
    @return_500_for_sever_error
    def get(self, id_):
        if user_role := get_user_role(id_):
            return self.send(response_type="SUCCESS", result=user_role)
        return self.send(response_type="NOT_FOUND")

    @api.doc("update user_role name")
    @api.expect(parser_post, parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def put(self, id_, **kwargs):
        if get_user_role(id_):
            if kwargs["auth_user"].is_admin():
                args = parser_post.parse_args()
                update_user_role(id_, args["name"])
                return self.send(response_type="NO_CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")

    @api.doc("delete a user_role")
    @api.expect(parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def delete(self, id_, **kwargs):
        if get_user_role(id_):
            if kwargs["auth_user"].is_admin():
                delete_user_role(id_)
                return self.send(response_type="NO_CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")
