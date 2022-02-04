import os
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_requests
from flask_restplus import Namespace, reqparse, Resource
from core.response import (
    exception_handler,
    CustomeResponse,
)
from core.models import User, AuthProvider, Session
from core.database import db

api = Namespace("oauth_users", description="Auth provider user related operations")


parser_create = reqparse.RequestParser()
parser_create.add_argument("provider_type", type=str, required=True)

parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers", required=True)


def verify_google_oauth2_refresh_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(
            token, google_auth_requests.Request(), os.getenv("GOOGLE_CLIENT_ID")
        )
        return idinfo["sub"], idinfo["name"]
    except Exception as e:
        # Invalid token
        pass


def verify_google_access_token(token):
    try:
        url = f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={token}"
        res = requests.get(url)
        res = res.json()
        return res["sub"], res["name"]

    except Exception as e:
        pass


def create_oauth2_user(provider_key, provider_type):
    new_user = User(os.getenv("GENERAL_ROLE_ID"))
    new_user.create()
    oauth2_user = AuthProvider(provider_key, provider_type, new_user.id)
    oauth2_user.create()
    return new_user.id


@api.route("/")
class OauthUser(Resource, CustomeResponse):
    @api.doc("login with Oauth2")
    @api.expect(parser_create, parser_auth)
    @exception_handler
    def post(self):
        """Create user by auth provider if not exist"""
        provider_type = parser_create.parse_args()["provider_type"]
        token = parser_auth.parse_args()["Authorization"]

        provider_key = None
        username = None
        if provider_type == "google":
            provider_key, username = verify_google_access_token(token)

        if provider_key:
            response_type = None
            user_id = None
            try:
                oauth2_user = AuthProvider.query.filter_by(
                    provider_key=provider_key
                ).first()
                user_id = oauth2_user.user_id
                response_type = "OK"

            except:
                user_id = create_oauth2_user(provider_key, "google")
                response_type = "CREATED"
            finally:
                user = User.query.filter_by(id=user_id).one()
                db.session.query(Session).filter(Session.user_id == user_id).delete()
                session = Session(user_id, token=token)
                session.create()
                result = {
                    "user": username,
                    "is_admin": 1 if user.is_admin() else 0,
                    "session": token,
                }

                return self.send(response_type=response_type, result=result)

        return self.send(response_type="BAD REQUEST")
