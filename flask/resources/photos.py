from flask_restplus import Namespace, Resource, fields
from core.google_drive_api import get_file_list

api = Namespace('photos', description='Photos related operations')

def upload_photo():
    return True


@api.route('/')
class Photos(Resource):
    @api.doc('list_photos')
    def get(self):
        '''List all photos'''
        get_file_list()
        return "photo"
    
    
    @api.doc('post a photo')
    def post(self):
        '''Upload a photo to Onedrive'''
        upload_photo()
        return "photo"

@api.route('/<id>')
@api.param('id', 'The photo identifier')
@api.response(404, 'photo not found')
class photo(Resource):
    @api.doc('get_photo')
    def get(self, id):
        '''Fetch a photo given its identifier'''
        return "photo"

    