import os
import os.path
import shutil
from app.core.file_manager import FileManager


def test_remove_file():
    dir = "test_remove_dir"
    file = "test_remove.txt"
    try:
        os.mkdir(dir)
    except:
        pass

    with open(f"{dir}/{file}", "w") as _:
        pass

    FileManager.remove(dir=dir, filename=file)
    assert not os.path.isfile(f"{dir}/{file}")
    shutil.rmtree(dir)


def test_():
    dir = "test_dir"
    files = ["test1.txt", "test2.txt", "test3.txt"]
    try:
        os.mkdir(dir)
    except:
        pass

    for file in files:
        with open(f"{dir}/{file}", "w") as _:
            pass

    assert set(FileManager.get_tmp_files(dir=dir)) == set(files)
    shutil.rmtree(dir)
