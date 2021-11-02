import traceback
import sqlalchemy
from flask_restplus import Namespace, reqparse
from core.resource import CustomResource
from core.models import UserRole
from core.database import db
from core.constants import response_status

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


@api.route("/")
class UserRoles(CustomResource):
    @api.doc("Get all user_roles")
    def get(self):
        try:
            return self.send(status=response_status.SUCCESS, result=get_user_roles())
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    @api.doc("create a new user_role")
    @api.expect(parser_post)
    def post(self):
        try:
            args = parser_post.parse_args()
            result, message = create_user_role(
                args["name"], args.get("description") or ""
            )
            if result:
                return self.send(status=response_status.CREATED, result=result.id)
            return self.send(status=response_status.FAIL, message=message)

        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)


@api.route("/<int:id_>")
@api.param("id_", "The user_role identifier")
class user_role(CustomResource):
    def get(self, id_):
        try:
            user_role = get_user_role(id_)
            if user_role:
                return self.send(status=response_status.SUCCESS, result=user_role)
            return self.send(status=response_status.NOT_FOUND)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    @api.doc("update user_role name")
    @api.expect(parser_post)
    def put(self, id_):
        try:
            if get_user_role(id_):
                args = parser_post.parse_args()
                update_user_role(id_, args["name"])
                return self.send(status=response_status.NO_CONTENT)
            return self.send(status=response_status.NOT_FOUND)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    @api.doc("delete a user_role")
    def delete(self, id_):
        try:
            if get_user_role(id_):
                delete_user_role(id_)
                return self.send(status=response_status.NO_CONTENT)
            return self.send(status=response_status.NOT_FOUND)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)
