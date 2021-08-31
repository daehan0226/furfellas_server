import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials



SCOPES = ['https://www.googleapis.com/auth/drive']
creds = None

def init_google_service():
    if os.path.exists('token.json'):
        print("google api auth token exists")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:    
            print("update google api auth token")
            token.write(creds.to_json())


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
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
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