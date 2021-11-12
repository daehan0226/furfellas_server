import string
import random
from datetime import datetime


def random_string(length):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def random_string_digits(length):
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def convert_to_datetime(string_datime):
    try:
        return datetime.strptime(string_datime, "%Y-%m-%d")
    except:
        return datetime.strptime(string_datime, "%Y-%m-%dT%H:%M:%S")
