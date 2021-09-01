import traceback
import werkzeug
import os
from flask_restplus import Namespace, Resource, reqparse
from werkzeug.datastructures import FileStorage
from apiclient.http import MediaFileUpload
from core.google_drive_api import get_file_list, get_service, get_folder_id
from core.resource import CustomResource

api = Namespace('photos', description='Photos related operations')

def upload_photo(file):
    image_id = None
    filename = werkzeug.secure_filename(file.filename)
    file_dir = f"tmp\{filename}"
    folder_id = get_folder_id()
    file_metadata = {
        'name': filename,    
        'parents': [folder_id],
    }
    file.save(file_dir)
    media = MediaFileUpload(file_dir, mimetype=file.content_type, resumable=True)
    service = get_service()
    result = service.files().create(body=file_metadata,
                            media_body=media,
                            fields='id').execute()
    image_id = result['id']
    return image_id

def save_photo():
    return 

def get_photos():
    return


parser_search = reqparse.RequestParser()
parser_search.add_argument('types', type=int, location="args", help="Alone or together", action='append')
parser_search.add_argument('actions', type=str, location="args", help="action ids or new actions", action='append')
parser_search.add_argument('locations', type=str, help='location ids or new locations', location="args", action='append')

parser_image = reqparse.RequestParser()
parser_image.add_argument("file", type=FileStorage, location='files')

@api.route('/')
class Photos(CustomResource):
    @api.doc('list_photos')
    @api.expect(parser_search)
    def get(self):
        '''List all photos'''
        try:            
            args = parser_search.parse_args()
            print(args)
            photos = get_photos()
            # folder_id = get_folder_id()
            # files = get_file_list(folder_id)
            return self.send(status=200, result=photos)

        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc('post a photo')
    @api.expect(parser_search, parser_image)
    def post(self):
        '''Upload a photo to Onedrive'''

        try:  
            photo_desc_args = parser_search.parse_args()
            photo_args = parser_image.parse_args()
            file = photo_args['file']
            image_id = upload_photo(file)
            # if image_id:
            #     save_photo()
        
        except:
            traceback.print_exc()
            return self.send(status=500)

@api.route('/<id>')
@api.param('id', 'The photo identifier')
@api.response(404, 'photo not found')
class photo(Resource):
    @api.doc('get_photo')
    def get(self, id):
        '''Fetch a photo given its identifier'''
        return "photo"

    