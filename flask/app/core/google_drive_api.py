from apiclient.http import MediaFileUpload
from apiclient import errors
import google_auth_httplib2
import httplib2
from googleapiclient import discovery
from google.oauth2 import service_account

from .. import celery
from app.core.errors import GoogleUploadError, GoogleFileNotFoundError


class GoogleDrive:
    def get_google_service_and_http_instance():
        try:
            credentials = service_account.Credentials.from_service_account_file(
                "client_secret.json"
            )
            scopedCreds = credentials.with_scopes(
                ["https://www.googleapis.com/auth/drive"]
            )
            service = discovery.build(
                "drive",
                "v3",
                credentials=scopedCreds,
            )
            http = google_auth_httplib2.AuthorizedHttp(
                scopedCreds,
                http=httplib2.Http(),
            )
            return service, http
        except Exception as e:
            print(e)

    @classmethod
    def get_file_id_by_name(cls, filename):
        service, http = cls.get_google_service_and_http_instance()
        try:
            results = (
                service.files()
                .list(q=f"name = '{filename}'", fields="nextPageToken, files(id, name)")
                .execute(http=http)
            )
            for item in results.get("files") or []:
                if item["name"] == filename:
                    return item["id"]
            raise GoogleFileNotFoundError(filename)
        except Exception as e:
            print(e)

    @classmethod
    @celery.task
    def upload(cls, folder_id, filename):
        service, http = cls.get_google_service_and_http_instance()
        try:
            file_metadata = {
                "name": filename,
                "parents": [folder_id],
            }
            media = MediaFileUpload(f"tmp/{filename}", resumable=True)
            result = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute(http=http)
            )
            if result["id"]:
                return result["id"]
            else:
                raise GoogleUploadError
        except Exception as e:
            print(e)
            return False

    @classmethod
    def print_file_metadata(cls, file_id):
        service, http = cls.get_google_service_and_http_instance()
        try:
            file = service.files().get(fileId=file_id).execute(http=http)
            print(
                f"file<id={file['id']}, name={file['name']}, mime_type={file['mimeType']}>"
            )
        except errors.HttpError as e:
            print(f"An error occurred: {e}")
