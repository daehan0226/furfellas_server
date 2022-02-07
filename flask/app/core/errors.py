class NoConfigError(Exception):
    def __init__(self, message="Provide config"):
        super().__init__(message)


class ConfigTypeError(Exception):
    def __init__(self, message="Provide a config name(one of prod, dev or test)"):
        super().__init__(message)


class GoogleFileNotFoundError(Exception):
    def __init__(self, filename, message="The file does not exist"):
        self.filename = filename
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}, file name : {self.filename}"


class GoogleUploadError(Exception):
    def __init__(self, message="Fail to upload file"):
        super().__init__(message)


class DatetimeConvertFormatError(Exception):
    def __init__(self, message="Could not convert this format"):
        super().__init__(message)


class StringIdsFormatError(Exception):
    def __init__(self, message="String ids must be like this, '1,2,3'"):
        super().__init__(message)


class FileError(Exception):
    def __init__(self, filename="", message="File related error occurred"):
        self.filename = filename
        self.message = message
        super().__init__(message)

    def __str__(self):
        if self.filename:
            return f"{self.message}, file name : {self.filename}"
        return f"{self.message}"


class FileSaveError(FileError):
    def __init__(self, filename="", message="Fail to save the file"):
        super().__init__(filename, message)


class FileRemoveError(FileError):
    def __init__(self, filename="", message="Fail to remove the file"):
        super().__init__(filename, message)


class FileExtractExtentionError(FileError):
    def __init__(self, filename="", message="Fail to extract file extention"):
        super().__init__(filename, message)
