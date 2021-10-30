from datetime import datetime
import time
import traceback
from threading import Thread
from flask_restplus import Namespace, reqparse

from core.resource import CustomResource
from core.models import User as UserModel
from core.models import Session as SessionModel

api = Namespace("sessions", description="Sessions related operations")



def expire_old_session_job():
    thread = Thread(target=expire_old_session)
    thread.daemon = True
    thread.start()


def expire_old_session():
    SESSION_VALID_TIME = 20
    SESSION_CHECK_TIME = 10
    while True:
        sessions = SessionModel.query().all()
        for session in sessions:
            if session.created_datetime - datetime.now() > SESSION_VALID_TIME:
                session.delete()
        time.sleep(SESSION_CHECK_TIME)


def get_user_if_verified(username, password):
    user = UserModel.query.filter_by(username=username).first()
    if user:
        if user.check_password(password):
            return user


def delete_session(id):
    return SessionModel.query.filter_by(user_id=id).delete()


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
                delete_session(user.id)
                session = SessionModel(user_id=user.id)
                session.create()
                return self.send(status=201, result=session.token)
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
            try:
                session = SessionModel.query.filter_by(token=args["Authorization"]).first()
                return self.send(status=200, result=session.id)
            except:
                return self.send(status=403)
        except:
            traceback.print_exc()
            return self.send(status=500)
