import os
from os import path, listdir
from os.path import dirname, abspath
from datetime import datetime
from sqlalchemy import exc
import werkzeug

from core.utils import random_string
from core.errors import FileRemoveError, FileSaveError, FileExtractExtentionError


class FileManager:
    tmp_dir = os.path.join(dirname(dirname(abspath(__file__))), "tmp")

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
            path = os.path.join(self.tmp_dir, self.name)
            self.file.save(path)
            return self.name
        except:
            raise FileSaveError(self.name)

    @classmethod
    def remove(cls, dir=None, filename=None):
        dir = cls.tmp_dir if dir is None else dir
        try:
            path = os.path.join(dir, filename)
            os.remove(path)
        except:
            raise FileRemoveError(filename)

    @classmethod
    def get_tmp_files(cls, dir=None):
        dir = cls.tmp_dir if dir is None else dir
        return [f for f in listdir(dir) if path.isfile(path.join(dir, f))]
