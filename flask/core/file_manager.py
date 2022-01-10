import uuid
from datetime import datetime
import werkzeug

from core.utils import random_string


class FileManager:
    def __init__(self, file):
        self.file = file
        self.name = self._gen_file_name()

    def _gen_file_name(self):
        suffix = datetime.now().strftime("%y%m%d_%H%M%S")
        return f"{suffix}_{random_string(6)}"

    def save(self):
        file_name_original = werkzeug.secure_filename(self.file.filename)
        extention = file_name_original.split(".")[-1]
        file_dir = f"tmp\{self.name}.{extention}"
        self.file.save(file_dir)
