import json
import os
import traceback

import werkzeug
from flask import Response, current_app, request

from app.core.constants import response


def login_required(f):
    def wrapper(*args, **kwargs):
        from app.core.models import User, Session, UserProfile

        def _get_test_admin():
            profile = UserProfile.query.filter_by(
                username=os.getenv("ADMIN_USER_NAME")
            ).one()
            user = User.query.get(profile.user_id)
            return user, profile.serialize

        def _get_user_from_token():
            user_id = Session.get_session(token=request.headers.get("Authorization"))[
                "user_id"
            ]
            user = User.query.get(user_id)
            profile = UserProfile.query.filter_by(user_id=user_id).one().serialize
            return user, profile

        def _get_user_from_gogle():
            from app.core.models.auth_provider import AuthProvider, GoogleOauthUser

            token = request.headers.get("Authorization")
            provider_key, username = GoogleOauthUser.return_userinfo_if_token_is_valid(
                token
            )
            auth = AuthProvider.query.filter_by(provider_key=provider_key).first()
            return User.query.get(auth.user_id), {"username": username}

        user = None
        user_profile = None
        if current_app.config["TESTING"]:
            try:
                user, user_profile = _get_user_from_token()
            except:
                user, user_profile = _get_test_admin()
            finally:
                return f(*args, **kwargs, auth_user=user, user_profile=user_profile)
        else:
            try:
                user, user_profile = _get_user_from_token()
            except Exception as e:
                try:
                    user, user_profile = _get_user_from_gogle()
                except:
                    pass
            if user is None or user_profile is None:
                response = CustomeResponse()
                return response.send(response_type="NO AUTH")
            return f(*args, **kwargs, auth_user=user, user_profile=user_profile)

    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper


def exception_handler(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except werkzeug.exceptions.BadRequest as e:
            print(f"400 bad request error : {e}")
            response = CustomeResponse()
            return response.send(
                response_type="BAD REQUEST",
            )
        except Exception as e:
            traceback.print_exc()
            print(f"500 error : {e}")
            response = CustomeResponse()
            return response.send(
                response_type="SEVER ERROR",
            )

    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper


class CustomeResponse:
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Credentials": "True",
    }

    def send(
        self,
        result=None,
        response_type=None,
        lang="en",
        additional_message=None,
    ):

        status = response.status[response_type]
        message = response.message[lang][response_type]

        if additional_message is not None:
            message += f"({additional_message})"

        response_body = {"result": result, "message": message}

        json_encode = json.JSONEncoder().encode
        return Response(
            json_encode(response_body),
            status=status,
            headers=self.headers,
            mimetype="application/json",
        )


def gen_dupilcate_keys_message(keys, lang="en"):
    if lang == "en":
        return f"The given {(', ').join(keys)} already exist(s)."
    if lang == "kr":
        return f"{(', ').join(keys)} (들)은 이미 존재합니다."
