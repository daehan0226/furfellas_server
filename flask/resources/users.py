import traceback
import sqlalchemy
from flask_restplus import Namespace, reqparse

from core.resource import CustomResource
from core.utils import token_required
from core.models import User as UserModel, UserRole as UserRoleModel
from core.database import db
from core.constants import response_status

api = Namespace("users", description="Users related operations")


def create_user(args) -> dict:
    general_user_role = UserRoleModel.query.filter_by(name="general").first()
    user = UserModel(
        args["username"], args.get("email"), args["password"], general_user_role.id
    )
    user.create()
    return user


def get_users(args) -> list:
    if args.get("username") is not None:
        users = UserModel.query.filter(
            UserModel.username.like(f"%{args.get('username')}%")
        )

    elif args.get("email") is not None:
        users = UserModel.query.filter(UserModel.email.like(f"%{args.get('email')}%"))
    else:
        users = UserModel.query.all()
    return [user.serialize for user in users]


def update_user(user, arg) -> None:
    if arg["password"] is not None:
        user.password = arg["password"]
    if arg["email"] is not None:
        user.email = arg["email"]
    db.session.commit()


def get_user_by_id(id_) -> dict:
    user = UserModel.query.get(id_)
    return user.serialize if user else None


def get_user_by_username(username) -> dict:
    user = UserModel.query.filter_by(username=username).first()
    return user.serialize if user else None


def get_user_by_email(email) -> dict:
    user = UserModel.query.filter_by(email=email).first()
    return user.serialize if user else None


def delete_user(id_) -> None:
    UserModel.query.filter_by(id=id_).delete()


def check_user_info_duplicates(args) -> list:
    result = []
    if args.get("username") is not None:
        if get_user_by_username(args.get("username")):
            result.append("username")

    if args.get("email") is not None:
        if get_user_by_email(args.get("email")):
            result.append("email")
    return result


parser_create = reqparse.RequestParser()
parser_create.add_argument("username", type=str, required=True, help="Unique user name")
parser_create.add_argument("email", type=str)
parser_create.add_argument("password", type=str, required=True, help="Password")

parser_delete = reqparse.RequestParser()
parser_delete.add_argument("ids", type=str, required=True, action="split")

parser_header = reqparse.RequestParser()
parser_header.add_argument("Authorization", type=str, location="headers")

parser_search = reqparse.RequestParser()
parser_search.add_argument("username", type=str, help="Unique user name")
parser_search.add_argument("email", type=str)


@api.route("/")
class Users(CustomResource):
    @api.expect(parser_search, parser_header)
    @token_required
    def get(self, **kwargs):
        """Get all users"""
        try:
            if kwargs["auth_user"]:
                if kwargs["auth_user"].is_admin():
                    args = parser_search.parse_args()
                    return self.send(
                        status=response_status.SUCCESS, result=get_users(args)
                    )
                return self.send(status=response_status.FORBIDDEN)
            return self.send(status=response_status.NO_AUTH)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    @api.doc("create a new user")
    @api.expect(parser_create)
    def post(self):
        """Create an user"""
        try:
            args = parser_create.parse_args()
            duplicate_keys = check_user_info_duplicates(args)
            if duplicate_keys:
                return self.send(
                    status=response_status.FAIL,
                    message=f"The given {duplicate_keys.join(', ')} exist(s).",
                )

            result = create_user(args)
            return self.send(status=response_status.CREATED, result=result.id)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)


@api.route("/<int:id_>")
class User(CustomResource):
    @api.doc("Get a user")
    @api.expect(parser_header)
    @token_required
    def get(self, id_, **kwargs):
        try:
            if kwargs["auth_user"]:
                if user := get_user_by_id(id_):
                    if kwargs["auth_user"].is_admin() or kwargs["auth_user"].id == id_:
                        return self.send(status=response_status.SUCCESS, result=user)
                return self.send(status=response_status.NOT_FOUND)
            return self.send(status=response_status.NO_AUTH)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    @api.expect(parser_header)
    @token_required
    def delete(self, id_, **kwargs):
        try:
            if kwargs["auth_user"]:
                if get_user_by_id(id_):
                    if kwargs["auth_user"].is_admin():
                        delete_user(id_)
                        return self.send(status=response_status.NO_CONTENT)
                    return self.send(status=response_status.FORBIDDEN)
                return self.send(status=response_status.NOT_FOUND)
            return self.send(status=response_status.NO_AUTH)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    @api.expect(parser_create, parser_header)
    @token_required
    def put(self, id_, **kwargs):
        try:
            if kwargs["auth_user"]:
                if get_user_by_id(id_):
                    if kwargs["auth_user"].is_admin():
                        args = parser_create.parse_args()
                        update_user(UserModel.query.get(id_), args)
                        return self.send(status=response_status.NO_CONTENT)
                    return self.send(status=response_status.FORBIDDEN)
                return self.send(status=response_status.NOT_FOUND)
            return self.send(status=response_status.NO_AUTH)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)
