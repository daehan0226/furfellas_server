from apiclient.http import MediaFileUpload

from core.database import db
from core.errors import GoogleUploadError, GoogleFileNotFoundError
from core.models.photo import Photo

from apiclient import errors

import google_auth_httplib2
import httplib2
from googleapiclient import discovery
from google.oauth2 import service_account


def get_google_service_and_http_instance():
    """
    https://github.com/googleapis/google-api-python-client/blob/main/docs/thread_safety.md

    The google-api-python-client library is built on top of the httplib2 library,
    which is not thread-safe. Therefore, if you are running as a multi-threaded application,
    each thread that you are making requests from must have its own instance of httplib2.Http().

    The easiest way to provide threads with their own httplib2.Http() instances is
    to either override the construction of it within the service object or
    to pass an instance via the http argument to method calls.
    """
    try:
        credentials = service_account.Credentials.from_service_account_file(
            "client_secret.json"
        )
        scopedCreds = credentials.with_scopes(["https://www.googleapis.com/auth/drive"])
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


def get_file_id_in_google_drvie_by_name(filename):
    service, http = get_google_service_and_http_instance()
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


def upload_to_google_drive(folder_id, filename):
    service, http = get_google_service_and_http_instance()
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


def print_file_metadata(file_id):
    service, http = get_google_service_and_http_instance()
    try:
        file = service.files().get(fileId=file_id).execute(http=http)
        print(
            f"file<id={file['id']}, name={file['name']}, mime_type={file['mimeType']}>"
        )
    except errors.HttpError as e:
        print(f"An error occurred: {e}")
