from flask_restplus import Namespace, reqparse
from flask_restplus import Resource
from core.response import (
    return_500_for_sever_error,
    return_401_for_no_auth,
    gen_dupilcate_keys_message,
    CustomeResponse,
)
from core.models import User as UserModel, UserRole as UserRoleModel
from core.database import db

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
    db.session.commit()


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

parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers")

parser_search = reqparse.RequestParser()
parser_search.add_argument("username", type=str, help="Unique user name")
parser_search.add_argument("email", type=str)


@api.route("/")
class Users(Resource, CustomeResponse):
    @api.expect(parser_search, parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def get(self, **kwargs):
        """Get all users"""
        if kwargs["auth_user"].is_admin():
            args = parser_search.parse_args()
            return self.send(response_type="SUCCESS", result=get_users(args))
        return self.send(response_type="FORBIDDEN")

    @api.doc("create a new user")
    @api.expect(parser_create)
    @return_500_for_sever_error
    def post(self):
        """Create an user"""
        args = parser_create.parse_args()
        if duplicate_keys := check_user_info_duplicates(args):
            return self.send(
                response_type="FAIL",
                additional_message=gen_dupilcate_keys_message(duplicate_keys),
            )
        result = create_user(args)
        return self.send(response_type="CREATED", result=result.id)


@api.route("/<int:id_>")
class User(Resource, CustomeResponse):
    @api.doc("Get a user")
    @api.expect(parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def get(self, id_, **kwargs):
        if user := get_user_by_id(id_):
            if kwargs["auth_user"].is_admin() or kwargs["auth_user"].id == id_:
                return self.send(response_type="SUCCESS", result=user)
        return self.send(response_type="NOT_FOUND")

    @api.expect(parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def delete(self, id_, **kwargs):
        if get_user_by_id(id_):
            if kwargs["auth_user"].is_admin():
                delete_user(id_)
                return self.send(response_type="NO_CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")

    @api.expect(parser_create, parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def put(self, id_, **kwargs):
        if get_user_by_id(id_):
            if kwargs["auth_user"].is_admin():
                args = parser_create.parse_args()
                update_user(UserModel.query.get(id_), args)
                return self.send(response_type="NO_CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")
