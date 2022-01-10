class NoConfigError(Exception):
    def __init__(self, message="Provide config"):
        self.message = message
        super().__init__(self.message)


class ConfigTypeError(Exception):
    def __init__(self, message="Provide a config name(one of prod, dev or test)"):
        self.message = message
        super().__init__(self.message)


class GoogleFileNotFoundError(Exception):
    def __init__(self, file_name, message="The file does not exist"):
        self.file_name = file_name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}, file name : {self.file_name}"


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


class FileSaveError(Exception):
    def __init__(self, message="Fail to save the file"):
        self.message = message
        super().__init__(self.message)
