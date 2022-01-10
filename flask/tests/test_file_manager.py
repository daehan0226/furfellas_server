import os
from datetime import datetime
from core.file_manager import FileManager


def test_gen_filename():
    file = FileManager(None)
    today = datetime.now().strftime("%y%m%d")

    assert today in file.name
