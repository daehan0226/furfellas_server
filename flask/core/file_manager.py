import os
from os import path, listdir
from datetime import datetime
from sqlalchemy import exc
import werkzeug

from core.utils import random_string
from core.errors import FileRemoveError, FileSaveError, FileExtractExtentionError


class FileManager:
    tmp_dir = "tmp"

    def __init__(self, file):
        self.file = file
        self.name = self._gen_filename()

    def _gen_filename(self):
        extention = self._extract_extention_from_filename()
        suffix = datetime.now().strftime("%y%m%d_%H%M%S")
        return f"{suffix}_{random_string(6)}.{extention}"

    def _extract_extention_from_filename(self):
        try:
            filename_original = werkzeug.secure_filename(self.file.filename)
            extention = filename_original.split(".")[-1:]
            return ".".join(extention)
        except:
            raise FileExtractExtentionError(filename_original)

    def save(self):
        try:
            self.file.save(f"{self.tmp_dir}\{self.name}")
        except:
            raise FileSaveError(self.name)

    @staticmethod
    def remove(filename):
        try:
            os.remove(f"{FileManager.tmp_dir}\{filename}")
        except:
            raise FileRemoveError(filename)

    @staticmethod
    def get_tmp_files():
        dir_path = FileManager.tmp_dir
        return [f for f in listdir(dir_path) if path.isfile(path.join(dir_path, f))]
