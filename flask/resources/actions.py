import sqlalchemy
from flask_restplus import Namespace, reqparse, Resource

from core.response import (
    CustomeResponse,
    return_500_for_sever_error,
    return_401_for_no_auth,
)
from core.models import Action as ActionModel
from core.database import db

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
        return False, f"Action name '{name}' already exsits."


def get_actions(name=None) -> list:
    if name is not None:
        actions = ActionModel.query.filter(ActionModel.name.like(f"%{name}%"))
    else:
        actions = ActionModel.query.all()
    return [action.serialize for action in actions]


def get_action(id_) -> dict:
    action = ActionModel.query.get(id_)
    return action.serialize if action else None


def update_action(id_, name):
    action = ActionModel.query.get(id_)
    action.name = name
    db.session.commit()


def delete_action(id_):
    ActionModel.query.filter_by(id=id_).delete()
    db.session.commit()


parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers")


@api.route("/")
class Actions(Resource, CustomeResponse):
    @api.doc("Get all actions")
    @api.expect(parser_search)
    @return_500_for_sever_error
    def get(self):
        args = parser_search.parse_args()
        return self.send(response_type="SUCCESS", result=get_actions(name=args["name"]))

    @api.doc("create a new action")
    @api.expect(parser_post, parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def post(self, **kwargs):
        if kwargs["auth_user"].is_admin():
            args = parser_post.parse_args()
            result, message = creat_action(args["name"])
            if result:
                return self.send(response_type="CREATED", result=result.id)
            return self.send(response_type="FAIL", additional_message=message)
        return self.send(response_type="FORBIDDEN")


@api.route("/<int:id_>")
@api.param("id_", "The action identifier")
class Action(Resource, CustomeResponse):
    @return_500_for_sever_error
    def get(self, id_):
        if action := get_action(id_):
            return self.send(response_type="SUCCESS", result=action)
        return self.send(response_type="NOT_FOUND")

    @api.doc("update action name")
    @api.expect(parser_post, parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def put(self, id_, **kwargs):
        if get_action(id_):
            if kwargs["auth_user"].is_admin():
                args = parser_post.parse_args()
                update_action(id_, args["name"])
                return self.send(response_type="NO_CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")

    @api.doc("delete an action")
    @api.expect(parser_auth)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def delete(self, id_, **kwargs):
        if get_action(id_):
            if kwargs["auth_user"].is_admin():
                delete_action(id_)
                return self.send(response_type="NO_CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")
