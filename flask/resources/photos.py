import traceback
import werkzeug
import os
from flask_restplus import Namespace, Resource, reqparse
from werkzeug.datastructures import FileStorage
from apiclient.http import MediaFileUpload
from core.google_drive_api import get_file_list, get_service, get_folder_id
from core.resource import CustomResource, json_serializer
from core.db import insert_photo, insert_photo_action, insert_photo_location, search_photos, get_photo_actions, get_photo_locations
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

def save_photo(image_id, args):
    try:
        type = args.get('types') or 0
        actions = args.get('actions') or []
        locations = args.get('locations') or []
        description = args.get('description') or ""
        photo_id = insert_photo(int(type), description, image_id)
        
        if actions: 
            insert_photo_action(photo_id, actions)
        if locations:
            insert_photo_location(photo_id, locations)

    except:
        traceback.print_exc()
        return False

def get_photos(args):
    try:            
        photos = search_photos()
        for photo in photos:
            photo['datetime'] = json_serializer(photo['datetime'])
            photo['upload_datetime'] = json_serializer(photo['upload_datetime'])
            photo["actions"] = get_photo_actions(photo["id"])
            photo["locations"] = get_photo_locations(photo["id"])
            
        return photos
    except:
        traceback.print_exc()
        return False


parser_search = reqparse.RequestParser()
parser_search.add_argument('types', type=int, location="args", help="Alone or together", action='append')
parser_search.add_argument('actions', type=str, location="args", help="action ids or new actions", action='append')
parser_search.add_argument('locations', type=str, help='location ids or new locations', location="args", action='append')
parser_search.add_argument('size', type=str, help='Photo count', location="args")

parser_create = reqparse.RequestParser()
parser_create.add_argument("file", type=FileStorage, location='files', required=True)
parser_create.add_argument('types', type=str, location="form", help="Alone or together", action='append')
parser_create.add_argument('actions', type=str, location="form", help="action ids or new actions", action='append')
parser_create.add_argument('locations', type=str, help='location ids or new locations', location="form", action='append')
parser_create.add_argument('description', type=str, help='photo description', location="form")
parser_create.add_argument('date', type=str, help='date of photo taken', location="form")

@api.route('/')
class Photos(CustomResource):
    @api.doc('list_photos')
    @api.expect(parser_search)
    def get(self):
        '''List all photos'''
        try:            
            args = parser_search.parse_args()
            photos = get_photos(args)
            return self.send(status=200, result=photos)

        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc('post a photo')
    @api.expect(parser_create)
    def post(self):
        '''Upload a photo to Onedrive'''
        try:  
            args = parser_create.parse_args()
            image_id = upload_photo(args['file'])

            if image_id:
                save_photo(image_id, args)

            return self.send(status=201)
        
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

    