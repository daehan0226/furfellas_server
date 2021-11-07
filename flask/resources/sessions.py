import os
import time
import traceback
from datetime import datetime
from threading import Thread
from dotenv import load_dotenv

from dateutil.relativedelta import relativedelta
from flask_restplus import Namespace, reqparse, Resource

from core.response import (
    CustomeResponse,
    return_500_for_sever_error,
    return_404_for_no_auth,
)
from core.models import User as UserModel
from core.models import Session as SessionModel
from core.database import get_db_session, db

api = Namespace("sessions", description="Sessions related operations")


APP_ROOT = os.path.join(os.path.dirname(__file__), "..")
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)


SESSION_CHECK_TIME_SECONDS = int(os.getenv("SESSION_CHECK_TIME_HOURS")) * 3600
SESSION_VALID_TIME_SECONDS = int(os.getenv("SESSION_VALID_TIME_HOURS")) * 3600


def create_session(user_id):
    return SessionModel(user_id=user_id).create()


def get_session(user_id=None, token=None):
    if user_id is not None:
        session = SessionModel.query.filter_by(user_id=user_id).first()
    elif token is not None:
        session = SessionModel.query.filter_by(token=token).first()
    return session.serialize if session else None


def expire_old_session_job():
    thread = Thread(target=expire_old_session)
    thread.daemon = True
    thread.start()


def expire_old_session():
    while True:
        try:
            db_scoped_session = get_db_session()
            db_session = db_scoped_session()
            sessions = db_session.query(SessionModel).all()
            for session in sessions:
                expire_datetime = session.created_datetime + relativedelta(
                    seconds=SESSION_VALID_TIME_SECONDS
                )
                if expire_datetime < datetime.now():
                    db_session.query(SessionModel).filter_by(id=session.id).delete()
                    db_session.commit()
            time.sleep(SESSION_CHECK_TIME_SECONDS)
            db_scoped_session.remove()
        except:
            traceback.print_exc()
            break


def get_user_if_verified(username, password):
    user = UserModel.query.filter_by(username=username).first()
    if user:
        if user.check_password(password):
            return user
    return None


def delete_session(id_=None, token=None):
    if id_ is not None:
        SessionModel.query.filter_by(user_id=id_).delete()
    elif token is not None:
        SessionModel.query.filter_by(token=token).delete()
    db.session.commit()


parser_create = reqparse.RequestParser()
parser_create.add_argument("username", type=str, required=True, help="Unique username")
parser_create.add_argument("password", type=str, required=True, help="Password")

parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers")


@api.route("/")
@api.response(401, "Session not found")
class Session(Resource, CustomeResponse):
    @api.expect(parser_create)
    @return_500_for_sever_error
    def post(self):
        """Create a session after verifying user info"""
        args = parser_create.parse_args()
        if user := get_user_if_verified(args["username"], args["password"]):
            delete_session(id_=user.id)
            result = {
                "user": user.username,
                "is_admin": 1 if user.is_admin() else 0,
                "session": create_session(user.id).token,
            }
            return self.send(response_type="CREATED", result=result)
        return self.send(
            response_type="FAIL", additional_message="Check your id and password."
        )

    @api.expect(parser_auth)
    @return_404_for_no_auth
    @return_500_for_sever_error
    def delete(self, **kwargs):
        if kwargs["auth_user"] is not None:
            delete_session(id_=kwargs["auth_user"].id)
            return self.send(response_type="NO_CONTENT")
        return self.send(response_type="NOT_FOUND")


@api.route("/validate")
class SessionVlidation(Resource, CustomeResponse):
    @api.expect(parser_auth)
    @return_404_for_no_auth
    @return_500_for_sever_error
    def get(self, **kwargs):
        """Check if session is valid"""
        if kwargs["auth_user"] is not None:
            result = {
                "user": kwargs["auth_user"].username,
                "is_admin": 1 if kwargs["auth_user"].is_admin() else 0,
            }
            return self.send(response_type="SUCCESS", result=result)
        return self.send(response_type="FAIL")
