import string
import random
from datetime import datetime
from app.core.errors import DatetimeConvertFormatError, StringIdsFormatError
from app.core.constants.response import status_code_msg


def random_string(length):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def random_string_digits(length):
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def convert_to_datetime(string_datime):

    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(string_datime, fmt)
        except ValueError:
            pass
    raise DatetimeConvertFormatError


def convert_str_ids_to_int_ids_tuple(str_ids):
    if str_ids:
        try:
            return (int(id_) for id_ in str_ids.split(","))
        except ValueError:
            raise StringIdsFormatError
    else:
        return None


def set_doc_responses(*responses):
    return {response: status_code_msg[response] for response in responses}
