import traceback
from flask_restplus import Namespace, reqparse
from core.resource import CustomResource

from core.models import Action as ActionModel
from core.database import db

api = Namespace("actions", description="actions related operations")


parser_action_name = reqparse.RequestParser()
parser_action_name.add_argument("name", type=str, help="action name")


parser_post = reqparse.RequestParser()
parser_post.add_argument("name", type=str, required=True, help="action name")


def creat_action(name):
    action = ActionModel(name)
    return action.create()


def get_actions(id=None, name=None):
    result = None
    if id is not None:
        result = ActionModel.query.get(id)
    elif name is not None:
        result = ActionModel.query.filter_by(name=name)
    else:
        result = ActionModel.query.all()
    return [action.serialize for action in result]


def get_action(id=None, name=None):
    if id is not None:
        action = ActionModel.query.get(id)
    elif name is not None:
        action = ActionModel.query.filter_by(name=name).first()
    else:
        return None

    return action.serialize if action else None


def update_action(id, name):
    try:
        action = ActionModel.query.get(id)
        action.name = name
        print(db.session.commit())
        return True
    except:
        return False


def delete_action(id=None, name=None):
    if id is not None:
        ActionModel.query.filter_by(id=id).delete()
    elif name is not None:
        ActionModel.query.filter_by(name=name).delete()
    db.session.commit()


@api.route("/")
class Actions(CustomResource):
    @api.doc("Get all actions")
    def get(self):
        try:
            actions = get_actions()
            if actions is None:
                return self.send(status=500)
            return self.send(status=200, result=actions)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("create a new action")
    @api.expect(parser_post)
    def post(self):
        try:
            args = parser_post.parse_args()
            result = creat_action(args["name"])
            if result is None:
                return self.send(status=500)
            return self.send(status=201, result=result)

        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("create a new action")
    @api.expect(parser_action_name)
    def delete(self):
        try:
            args = parser_action_name.parse_args()
            result = delete_action(name=args["name"])
            if result is None:
                return self.send(status=500)
            return self.send(status=204)

        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/<int:id_>")
@api.param("id_", "The action identifier")
class Action(CustomResource):
    def get(self, id_):
        try:
            action = get_action(id=id_)
            if action:
                return self.send(status=200, result=action)
            return self.send(status=404)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("update action name")
    @api.expect(parser_post)
    def put(self, id_):
        try:
            args = parser_post.parse_args()
            action = get_action(id=id_)
            if action:
                update_action(id_, args["name"])
                return self.send(status=204)
            return self.send(status=404)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("delete an action")
    def delete(self, id_):
        try:
            result = delete_action(id_=id_)
            if result is None:
                return self.send(status=500)
            return self.send(status=204)

        except:
            traceback.print_exc()
            return self.send(status=500)
