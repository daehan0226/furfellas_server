from flask_restplus import Namespace, reqparse, Resource

from app.core.response import (
    CustomeResponse,
    exception_handler,
    login_required,
)
from app.core.models import User, UserProfile, Session as SessionModel
from app.core.utils import set_doc_responses

api = Namespace("sessions", description="Sessions related operations")


parser_create = reqparse.RequestParser()
parser_create.add_argument("username", type=str, required=True, help="Unique username")
parser_create.add_argument("password", type=str, required=True, help="Password")

parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers")


@api.route("/")
class Session(Resource, CustomeResponse):
    @api.doc(responses=set_doc_responses(201, 400, 500))
    @api.expect(parser_create)
    @exception_handler
    def post(self):
        """Create a session after verifying user info"""
        args = parser_create.parse_args()
        if user_profile := UserProfile.get_user_if_verified(
            args["username"], args["password"]
        ):
            user = User.query.get(user_profile.user_id)
            SessionModel.delete(id_=user.id)
            result = {
                "user": user_profile.username,
                "is_admin": 1 if user.is_admin() else 0,
                "session": SessionModel.create(user.id).token,
            }
            return self.send(response_type="CREATED", result=result)
        return self.send(
            response_type="BAD REQUEST",
            additional_message="Check your id and password.",
        )

    @api.doc(responses=set_doc_responses(204, 404, 500))
    @api.expect(parser_auth)
    @login_required
    @exception_handler
    def delete(self, **kwargs):
        """Delete the session"""
        if kwargs["auth_user"] is not None:
            SessionModel.delete(id_=kwargs["auth_user"].id)
            return self.send(response_type="NO CONTENT")
        return self.send(response_type="NOT FOUND")


@api.route("/validate")
class SessionVlidation(Resource, CustomeResponse):
    @api.doc(responses=set_doc_responses(200, 400, 500))
    @api.expect(parser_auth)
    @login_required
    @exception_handler
    def get(self, **kwargs):
        """Check if session is valid"""
        if kwargs["auth_user"] is not None:
            result = {
                "user": kwargs["user_profile"]["username"],
                "is_admin": 1 if kwargs["auth_user"].is_admin() else 0,
            }
            return self.send(response_type="OK", result=result)
        return self.send(response_type="BAD REQUEST")
