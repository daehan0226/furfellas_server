import os.path
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


SCOPES = ['https://www.googleapis.com/auth/drive']
creds = None

def init_google_service():
    global creds
    creds = ServiceAccountCredentials.from_json_keyfile_name(
            'client_secret.json', scopes=SCOPES)


def get_folder_id(folder_name='furfellas'):
    service = get_service()
    results = service.files().list(
        q=f"name = '{folder_name}'",
        fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        return False
    else:
        for item in items:
            if item['name'] == folder_name:
                return item['id']
    return False

def get_service():
    global creds
    service = build('drive', 'v3', credentials=creds)
    return service


def get_file_list(folder_id):
    # Call the Drive v3 API
    service = get_service()
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
    return items