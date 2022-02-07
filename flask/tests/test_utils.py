import pytest
from datetime import datetime
from app.core.utils import convert_to_datetime, convert_str_ids_to_int_ids_tuple
from app.core.errors import DatetimeConvertFormatError


def test_convert_to_datetime():
    str_datetime = "2022-1-7"

    assert convert_to_datetime(str_datetime) == datetime(2022, 1, 7)


def test_convert_to_datetime_wrong_foramt():

    with pytest.raises(DatetimeConvertFormatError):
        convert_to_datetime("2022.1.7")


def test_convert_str_ids_to_int_ids_tuple():
    str_ids = "1,2,3"
    assert sorted(convert_str_ids_to_int_ids_tuple(str_ids)) == sorted((1, 2, 3))


def test_convert_str_ids_to_int_ids_tuple_wrong_format():
    str_ids = "1 2 3"
    with pytest.raises(ValueError):
        assert sorted(convert_str_ids_to_int_ids_tuple(str_ids)) == sorted((1, 2, 3))
