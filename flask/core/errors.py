class NoConfigError(Exception):
    def __init__(self, message="Provide config"):
        self.message = message
        super().__init__(self.message)


class ConfigTypeError(Exception):
    def __init__(self, message="Provide a config name(one of prod, dev or test)"):
        self.message = message
        super().__init__(self.message)


class GoogleFileNotFoundError(Exception):
    def __init__(self, filename, message="The file does not exist"):
        self.filename = filename
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}, file name : {self.filename}"


class GoogleUploadError(Exception):
    def __init__(self, message="Fail to upload file"):
        self.message = message
        super().__init__(self.message)


class DatetimeConvertFormatError(Exception):
    def __init__(self, message="Could not convert this format"):
        self.message = message
        super().__init__(self.message)


class StringIdsFormatError(Exception):
    def __init__(self, message="String ids must be like this, '1,2,3'"):
        self.message = message
        super().__init__(self.message)


class FileError(Exception):
    def __init__(
        self, filename, message="File related error occurred", *args, **kwargs
    ):
        self.filename = filename
        self.message = message
        super().__init__(message, *args, **kwargs)

    def __str__(self):
        return f"{self.message}, file name : {self.filename}"


class FileSaveError(FileError):
    def __init__(self, filname, message="Fail to save the file"):
        self.filename = filname
        self.message = message


class FileRemoveError(FileError):
    def __init__(self, filename, message="Fail to remove the file"):
        self.filename = filename
        self.message = message


class FileExtractExtentionError(FileError):
    def __init__(self, filename, message="Fail to extract file extention"):
        self.filename = filename
        self.message = message
