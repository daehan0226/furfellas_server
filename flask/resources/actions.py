import traceback
from flask_restplus import Namespace, reqparse
from core.resource import CustomResource
from core import db 

api = Namespace('actions', description='actions related operations')


parser_post = reqparse.RequestParser()
parser_post.add_argument('name', type=str, required=True, help="action name")

def get_actions():
    try:
        actions = db.get_actions()
        return actions
    except:
        traceback.print_exc()
        return None

def insert_action(name):
    try:
        result = db.insert_action(name)
        return result
    except:
        traceback.print_exc()
        return None

@api.route('/')
class Actions(CustomResource):
    @api.doc('Get all actions')
    def get(self):
        try:            
            actions = get_actions()
            if actions is None:
                return self.send(status=500)
            return self.send(status=200, result=actions)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc('create a new action')
    @api.expect(parser_post)
    def post(self):
        try:  
            args = parser_post.parse_args()
            result = insert_action(args['name'])
            if result is None:            
                return self.send(status=500)
            return self.send(status=201)
        
        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route('/<int:id_>')
@api.param('id_', 'The action identifier')
class Action(CustomResource):
    @api.doc('update action name')
    @api.expect(parser_post)
    def put(self, id_):
        try:            
            args = parser_post.parse_args()
            result = db.update_action(id_, args['name'])
            if result is None:
                return self.send(status=500)
            return self.send(status=203)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc('delete an action')
    def delete(self, id_):
        try:  
            result= db.delete_action(id_)
            if result is None:            
                return self.send(status=500)
            return self.send(status=200)
        
        except:
            traceback.print_exc()
            return self.send(status=500)