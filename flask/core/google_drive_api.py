import os.path
from googleapiclient.discovery import build
import werkzeug
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.http import MediaFileUpload
from flask import current_app

from core.errors import GoogleUploadError, GoogleFileNotFoundError


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

    def get_file_id_by_name(self, file_name):
        results = (
            self.service.files()
            .list(q=f"name = '{file_name}'", fields="nextPageToken, files(id, name)")
            .execute()
        )
        for item in results.get("files") or []:
            if item["name"] == file_name:
                return item["id"]
        raise GoogleFileNotFoundError(file_name)

    def upload_photo(self, file):
        try:
            filename = werkzeug.secure_filename(file.filename)
            file_dir = f"tmp\{filename}"
            file.save(file_dir)
            if folder_id := self.get_file_id_by_name("furfellas"):
                file_metadata = {
                    "name": filename,
                    "parents": [folder_id],
                }
                media = MediaFileUpload(
                    file_dir, mimetype=file.content_type, resumable=True
                )
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
