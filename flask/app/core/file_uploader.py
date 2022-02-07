from queue import Queue
from threading import Event
import concurrent.futures

from app.core.models import Photo
from app.core.google_drive_api import GoogleDrive
from app.core.file_manager import FileManager

pipeline = Queue(maxsize=20)
event = Event()


class FileUploader:
    def file_producer(cls, queue, event):
        print("ppp")
        while not event.is_set():  # when 0(initial value/ after calling clear method)

            files = FileManager.get_tmp_files()
            # files = Photo.get_photos_to_upload()
            for file in files:
                print(f"File producer got file: {file}")
                queue.put(file)

    def file_consumer(cls, queue, event):
        print("c")
        while not event.is_set() or not queue.empty():
            filename = queue.get()
            print(f"upload file : {filename}")
            GoogleDrive.upload(GoogleDrive.get_file_id_by_name("furfellas"), filename)

    @classmethod
    def start_thread(cls):
        """
        Python Event
        Flag  initaial value 0
        set() -> 1, clear() -> 0, wait(1 -> return, 0 -> wait), is_set() -> current flag value
        """
        global pipeline
        global event
        print("file uploaer thread started")

        while True:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                executor.submit(cls.file_producer, pipeline, event)
                executor.submit(cls.file_consumer, pipeline, event)

                event.set()  # finish thread pool
            event.clear()  # reset flag to 0 to start agian
