import string
import random
import traceback
from flask_restplus import Namespace, reqparse

from core.db import redis_store, get_user
from .users import get_user_if_verified
from core.utils import token_required, random_string_digits
from core.resource import CustomResource

api = Namespace('sessions', description='Sessions related operations')


parser_create = reqparse.RequestParser()
parser_create.add_argument('username', type=str, required=True, help='Unique username')
parser_create.add_argument('password', type=str, required=True, help='Password')

parser_header = reqparse.RequestParser()
parser_header.add_argument('Authorization', type=str, required=True, location='headers')

@api.route('/')
@api.response(401, 'Session not found')
class Session(CustomResource):  
    @api.doc('create_session')
    @api.expect(parser_create)
    def post(self):
        '''Create a session after verifying user info '''
        try:
            args = parser_create.parse_args()
            user = get_user_if_verified(args["username"], args["password"])
            if user:
                session_id = random_string_digits(30)
                redis_store.set(name=session_id, value=user["id"], ex=60*60*24)
                user_data = get_user(id_=user["id"])
                is_admin = 1 if user_data["user_type"] == 0 else 0
                result = {
                    "session": session_id,
                    "name": user_data["name"],
                    "is_admin": is_admin
                }
                return self.send(status=201, result=result)
            else:
                return self.send(status=400, message="Check your id and password.")
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc('delete_session')
    @api.expect(parser_header)
    def delete(self):
        '''User logout'''
        try:
            args = parser_header.parse_args()
            redis_store.delete(args["Authorization"])
            return self.send(status=200)
        except:
            traceback.print_exc()
            return self.send(status=500)

@api.route('/validate')
@api.response(401, 'Session is not valid')
class SessionVlidation(CustomResource):
    @api.doc('get_session')
    @api.expect(parser_header)
    @token_required
    def get(self, **kwargs):
        '''Check if session is valid'''
        try:
            user={}
            status = 401
            if kwargs["user_info"] is not None:
                status = 200
                user["name"] = kwargs["user_info"]["name"]
                user["is_admin"] = 1 if kwargs["user_info"]["user_type"] == 0 else 0
            return self.send(status=status, result=user)
        except:
            traceback.print_exc()
            return self.send(status=500)
