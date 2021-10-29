import string
import random
import traceback
from flask_restplus import Namespace, reqparse

from core.utils import token_required, random_string_digits
from core.resource import CustomResource
from core.models import User as UserModel

api = Namespace("sessions", description="Sessions related operations")

sessions = {}


def get_user_if_verified(username, password):
    user = UserModel.query.filter_by(username=username).first()
    if user:
        if user.check_password(password):
            return user


parser_create = reqparse.RequestParser()
parser_create.add_argument("username", type=str, required=True, help="Unique username")
parser_create.add_argument("password", type=str, required=True, help="Password")

parser_header = reqparse.RequestParser()
parser_header.add_argument("Authorization", type=str, required=True, location="headers")


@api.route("/")
@api.response(401, "Session not found")
class Session(CustomResource):
    @api.doc("create_session")
    @api.expect(parser_create)
    def post(self):
        """Create a session after verifying user info"""
        try:
            args = parser_create.parse_args()
            user = get_user_if_verified(args["username"], args["password"])
            if user:
                session_id = random_string_digits(30)
                global sessions
                sessions = {session_id: user.id}
                return self.send(status=201, result=session_id)
            else:
                return self.send(status=400, message="Check your id and password.")
        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/validate")
class SessionVlidation(CustomResource):
    @api.doc("get_session")
    @api.expect(parser_header)
    def get(self):
        """Check if session is valid"""
        try:
            args = parser_header.parse_args()
            global sessions
            try:
                user_id = sessions[args.get("Authorization")]
                return self.send(status=200, result=user_id)
            except:
                return self.send(status=403)
        except:
            traceback.print_exc()
            return self.send(status=500)
