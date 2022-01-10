import os.path
from googleapiclient.discovery import build
import werkzeug
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.http import MediaFileUpload

from core.database import db
from core.errors import GoogleUploadError, GoogleFileNotFoundError
from core.models.photo import Photo

from apiclient import errors


class SingletonInstane:
    __instance = None

    @classmethod
    def __getInstance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__getInstance
        return cls.__instance


class GoogleManager(SingletonInstane):
    def __init__(self):
        self.service = build(
            "drive",
            "v3",
            credentials=ServiceAccountCredentials.from_json_keyfile_name(
                "client_secret.json", scopes=["https://www.googleapis.com/auth/drive"]
            ),
        )

    def get_file_id_by_name(self, filename):
        results = (
            self.service.files()
            .list(q=f"name = '{filename}'", fields="nextPageToken, files(id, name)")
            .execute()
        )
        for item in results.get("files") or []:
            if item["name"] == filename:
                return item["id"]
        raise GoogleFileNotFoundError(filename)

    def upload_photo(self, filename):
        try:
            file_metadata = {
                "name": filename,
                "parents": [self.get_file_id_by_name("furfellas")],
            }
            media = MediaFileUpload(f"tmp/{filename}", resumable=True)
            result = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )
            if result["id"]:
                return result["id"]
            else:
                raise GoogleUploadError
        except Exception as e:
            print(e)
            return False

    def print_file_metadata(self, file_id):
        try:
            file = self.service.files().get(fileId=file_id).execute()
            print(
                f"file<id={file['id']}, name={file['name']}, mime_type={file['mimeType']}>"
            )
        except errors.HttpError as e:
            print(f"An error occurred: {e}")
