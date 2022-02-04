import sqlalchemy
from flask_restplus import Namespace, reqparse, Resource

from core.response import (
    CustomeResponse,
    exception_handler,
    login_required,
)
from core.models import Action as ActionModel
from core.database import db
from core.utils import set_doc_responses

api = Namespace("actions", description="actions related operations")

parser_post = reqparse.RequestParser()
parser_post.add_argument(
    "name", type=str, required=True, help="New action name", location="json"
)

parser_search = reqparse.RequestParser()
parser_search.add_argument(
    "name", type=str, help="Find actions that includes the given name"
)

parser_auth = reqparse.RequestParser()
parser_auth.add_argument(
    "Authorization",
    type=str,
    location="headers",
    required=True,
    help="Only admin can create a new action",
)


def creat_action(name):
    try:
        action = ActionModel(name)
        action.create()
        return action, ""
    except sqlalchemy.exc.IntegrityError as e:
        return False, f"Action name '{name}' already exists."


def get_actions(name=None) -> list:
    if name is not None:
        actions = ActionModel.query.filter(ActionModel.name.like(f"%{name}%"))
    else:
        actions = ActionModel.query.all()
    return [action.serialize for action in actions]


def get_action_by_name(name) -> object:
    return ActionModel.query.filter_by(name=name).first()


def update_action(id_, name):
    action = ActionModel.query.get(id_)
    action.name = name
    db.session.commit()


@api.route("/")
class Actions(Resource, CustomeResponse):
    @api.doc(responses=set_doc_responses(200, 500))
    @api.expect(parser_search)
    @exception_handler
    def get(self):
        """Get all actions with filter by name if given."""
        args = parser_search.parse_args()
        return self.send(response_type="OK", result=get_actions(name=args["name"]))

    @api.doc(responses=set_doc_responses(200, 401, 403, 409, 500))
    @api.expect(parser_post, parser_auth)
    @login_required
    @exception_handler
    def post(self, **kwargs):
        """Create a new action."""
        if kwargs["auth_user"].is_admin():
            args = parser_post.parse_args()
            result, message = creat_action(args["name"])
            if result:
                return self.send(response_type="CREATED", result=result.id)
            return self.send(response_type="CONFLICT", additional_message=message)
        return self.send(response_type="FORBIDDEN")


@api.route("/<int:id_>")
class Action(Resource, CustomeResponse):
    @api.doc(
        params={"id_": "The action identifier"},
        responses=set_doc_responses(200, 404, 500),
    )
    @exception_handler
    def get(self, id_):
        """Get action by id value."""
        if action := ActionModel.get_by_id(id_):
            return self.send(response_type="OK", result=action.serialize)
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 401, 403, 404, 409, 500))
    @api.expect(parser_post, parser_auth)
    @login_required
    @exception_handler
    def put(self, id_, **kwargs):
        """Update the name of the action."""
        if action := ActionModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                args = parser_post.parse_args()
                if action.name == args["name"]:
                    return self.send(response_type="NO CONTENT")
                if get_action_by_name(args["name"]):
                    return self.send(
                        response_type="CONFLICT",
                        additional_message=f"{args['name']} already exists ",
                    )
                update_action(id_, args["name"])
                return self.send(response_type="NO CONTENT")

            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")

    @api.doc(responses=set_doc_responses(204, 401, 403, 404, 500))
    @api.expect(parser_auth)
    @login_required
    @exception_handler
    def delete(self, id_, **kwargs):
        """Delete the action."""
        if ActionModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                ActionModel.delete_by_id(id_)
                return self.send(response_type="NO CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT FOUND")
