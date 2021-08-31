from flask_restplus import Namespace, Resource, fields
from apiclient.http import MediaFileUpload
from core.google_drive_api import get_file_list, get_service, get_folder_id

api = Namespace('photos', description='Photos related operations')

def upload_photo():
    folder_id = get_folder_id()
    file_metadata = {
        'name': 'photo.jpeg',    
        'parents': [folder_id],
    }
    media = MediaFileUpload('files/photo.jpeg', mimetype='image/jpeg')
    service = get_service()
    service.files().create(body=file_metadata,
                            media_body=media,
                            fields='id').execute()
    return True


@api.route('/')
class Photos(Resource):
    @api.doc('list_photos')
    def get(self):
        '''List all photos'''
        folder_id = get_folder_id()
        files = get_file_list(folder_id)
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

    