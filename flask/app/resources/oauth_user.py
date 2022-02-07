from flask_restplus import Namespace, reqparse, Resource

from app.core.response import (
    exception_handler,
    CustomeResponse,
)
from app.core.models.auth_provider import GoogleOauthUser
from app.core.utils import set_doc_responses

api = Namespace("oauth_users", description="Auth provider user related operations")


parser_create = reqparse.RequestParser()
parser_create.add_argument("provider_type", type=str, required=True)

parser_auth = reqparse.RequestParser()
parser_auth.add_argument("Authorization", type=str, location="headers", required=True)


@api.route("/")
class OauthUser(Resource, CustomeResponse):
    @api.doc(responses=set_doc_responses(200, 201, 400, 500))
    @api.expect(parser_create, parser_auth)
    @exception_handler
    def post(self):
        """Create user by auth provider if not exist - Googel Oauth2"""
        provider_type = parser_create.parse_args()["provider_type"]
        token = parser_auth.parse_args()["Authorization"]

        if provider_type == "google":
            google_oauth = GoogleOauthUser(token)
            if not google_oauth.verify_token():
                return self.send(
                    response_type="BAD REQUEST",
                    additional_message="Please login in through Google first",
                )

            response_type = "OK"
            if not google_oauth.check_if_user_exists():
                response_type = "CREATED"
                google_oauth.create_user()

            result = {
                "user": google_oauth.username,
                "is_admin": 1 if google_oauth.is_admin() else 0,
                "session": token,
            }

            return self.send(response_type=response_type, result=result)

        return self.send(response_type="BAD REQUEST")
