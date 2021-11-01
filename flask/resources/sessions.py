import os
import re
import time
import traceback
from datetime import datetime
from threading import Thread

from dateutil.relativedelta import relativedelta
from flask_restplus import Namespace, reqparse

from core.resource import CustomResource
from core.models import User as UserModel
from core.models import Session as SessionModel
from core.database import get_db_session, db
from core.constants import response_status

api = Namespace("sessions", description="Sessions related operations")

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

parser_header = reqparse.RequestParser()
parser_header.add_argument("Authorization", type=str, required=True, location="headers")


@api.route("/")
@api.response(401, "Session not found")
class Session(CustomResource):
    @api.expect(parser_create)
    def post(self):
        """Create a session after verifying user info"""
        try:
            args = parser_create.parse_args()
            user = get_user_if_verified(args["username"], args["password"])
            if user:
                delete_session(id_=user.id)
                session = create_session(user.id)
                return self.send(status=response_status.CREATED, result=session.token)
            else:
                return self.send(
                    status=response_status.FAIL, message="Check your id and password."
                )
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)

    @api.expect(parser_header)
    def delete(self):
        try:
            args = parser_header.parse_args()
            token = args["Authorization"]
            if get_session(token=token):
                delete_session(token=token)
                return self.send(status=response_status.NO_CONTENT)
            else:
                return self.send(status=response_status.NOT_FOUND)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)


@api.route("/validate")
class SessionVlidation(CustomResource):
    @api.expect(parser_header)
    def get(self):
        """Check if session is valid"""
        try:
            args = parser_header.parse_args()
            session = get_session(token=args["Authorization"])
            if session:
                return self.send(
                    status=response_status.SUCCESS, result=session["user_id"]
                )
            else:
                return self.send(status=response_status.FAIL)
        except:
            traceback.print_exc()
            return self.send(status=response_status.SEVER_ERROR)
