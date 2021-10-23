import traceback
from flask_restplus import Namespace, reqparse
from core.resource import CustomResource
from core import db

api = Namespace("actions", description="actions related operations")


parser_action_name = reqparse.RequestParser()
parser_action_name.add_argument("name", type=str, help="action name")


parser_post = reqparse.RequestParser()
parser_post.add_argument("name", type=str, required=True, help="action name")


def insert_action(name):
    try:
        result = db.insert_action(name)
        return result
    except:
        traceback.print_exc()
        return None


@api.route("/")
class Actions(CustomResource):
    @api.doc("Get all actions")
    @api.expect(parser_action_name)
    def get(self):
        try:
            args = parser_action_name.parse_args()
            actions = db.get_actions(name=args["name"])
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
            result = insert_action(args["name"])
            if result is None:
                return self.send(status=500)
            return self.send(status=201)

        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("create a new action")
    @api.expect(parser_action_name)
    def delete(self):
        try:
            args = parser_action_name.parse_args()
            result = db.delete_action(name=args["name"])
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
            action = db.get_actions(id_=id_)
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
            result = db.update_action(id_, args["name"])
            if result is None:
                return self.send(status=500)
            return self.send(status=204)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("delete an action")
    def delete(self, id_):
        try:
            result = db.delete_action(id_=id_)
            if result is None:
                return self.send(status=500)
            return self.send(status=204)

        except:
            traceback.print_exc()
            return self.send(status=500)
