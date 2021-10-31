import traceback
import sqlalchemy
from flask_restplus import Namespace, reqparse

from core.resource import CustomResource
from core.models import Action as ActionModel
from core.database import db
from core.constants import response_status

api = Namespace("actions", description="actions related operations")

parser_post = reqparse.RequestParser()
parser_post.add_argument("name", type=str, required=True, help="action name")


parser_search = reqparse.RequestParser()
parser_search.add_argument("name", type=str, help="action name")


def creat_action(name):
    try:
        action = ActionModel(name)
        action.create()
        return action, ""
    except sqlalchemy.exc.IntegrityError as e:
        print(e)
        return False, f"Action name '{name}' already exsits."


def get_actions(name=None):
    if name is not None:
        actions = ActionModel.query.filter(ActionModel.name.like(f"%{name}%"))
    else:
        actions = ActionModel.query.all()
    return [action.serialize for action in actions]


def get_action(id_):
    action = ActionModel.query.get(id_)
    return action.serialize if action else None


def update_action(id_, name):
    action = ActionModel.query.get(id_)
    action.name = name
    db.session.commit()


def delete_action(id):
    ActionModel.query.filter_by(id=id).delete()


@api.route("/")
class Actions(CustomResource):
    @api.doc("Get all actions")
    @api.expect(parser_search)
    def get(self):
        try:
            args = parser_search.parse_args()
            return self.send(
                status=response_status.SUCCESS, result=get_actions(name=args["name"])
            )
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    @api.doc("create a new action")
    @api.expect(parser_post)
    def post(self):
        try:
            args = parser_post.parse_args()
            result, message = creat_action(args["name"])
            if result:
                return self.send(status=response_status.CREATED, result=result.id)
            return self.send(status=response_status.FAIL, message=message)

        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)


@api.route("/<int:id_>")
@api.param("id_", "The action identifier")
class Action(CustomResource):
    def get(self, id_):
        try:
            action = get_action(id_)
            if action:
                return self.send(status=response_status.SUCCESS, result=action)
            return self.send(status=response_status.NOT_FOUND)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    @api.doc("update action name")
    @api.expect(parser_post)
    def put(self, id_):
        try:
            args = parser_post.parse_args()
            action = get_action(id_)
            if action:
                update_action(id_, args["name"])
                return self.send(status=response_status.NO_CONTENT)
            return self.send(status=response_status.NOT_FOUND)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    @api.doc("delete an action")
    def delete(self, id_):
        try:
            action = get_action(id_)
            if action:
                delete_action(id_)
                return self.send(status=response_status.NO_CONTENT)
            return self.send(status=response_status.NOT_FOUND)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)
