import traceback
from flask_restplus import Namespace, reqparse

from core.resource import CustomResource
from core.utils import token_required
from core.models import User as UserModel
from core.database import db

api = Namespace("users", description="Users related operations")


def create_user(arg):
    user = UserModel(arg["username"], arg.get("email"), arg["password"])
    user.create()
    return user.id


def get_users():
    return [user.serialize for user in UserModel.query.all()]


def update_user(user, arg):
    try:
        user.password = arg["password"]
        user.email = arg["email"]
        db.session.commit()
        return True
    except:
        return False


def get_user(id=None, username=None):
    if id is not None:
        return UserModel.query.filter_by(id=id).first()
    elif username is not None:
        return UserModel.query.filter_by(username=username).first()
    else:
        return False  # rasie error


def delete_user(id):
    return UserModel.query.filter_by(id=id).delete()


parser_create = reqparse.RequestParser()
parser_create.add_argument("username", type=str, required=True, help="Unique user name")
parser_create.add_argument("email", type=str)
parser_create.add_argument("password", type=str, required=True, help="Password")

parser_delete = reqparse.RequestParser()
parser_delete.add_argument("ids", type=str, required=True, action="split")

parser_header = reqparse.RequestParser()
parser_header.add_argument("Authorization", type=str, required=True, location="headers")


@api.route("/")
class Users(CustomResource):
    def get(self):
        """Get all users"""
        try:
            return self.send(status=200, result=get_users())
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("create a new user")
    @api.expect(parser_create)
    def post(self):
        """Create an user"""
        try:
            args = parser_create.parse_args()
            user = get_user(username=args["username"])
            if user:
                return self.send(
                    status=400, message="The given username already exists."
                )

            result = create_user(args)
            if result:
                return self.send(status=201, result=result)
            else:
                return self.send(status=500)
        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/<int:id>")
class User(CustomResource):
    @api.doc("Get a user")
    def get(self, id):
        try:
            user = get_user(id=id)
            if user:
                return self.send(status=200, result=user.serialize)
            return self.send(status=404)
        except:
            traceback.print_exc()
            return self.send(status=500)

    def delete(self, id):
        try:
            if delete_user(id):
                return self.send(status=204)

            return self.send(status=404)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.expect(parser_create)
    def put(self, id):
        try:
            user = get_user(id=id)
            if user:
                args = parser_create.parse_args()
                result = update_user(user, args)
                if result:
                    return self.send(status=200, result=user.id)
                else:
                    return self.send(status=400)
            return self.send(status=404)

        except:
            traceback.print_exc()
            return self.send(status=500)
