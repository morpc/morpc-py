import datetime
import math

import numpy as np
import pandas as pd
import pytest

from morpc.utils import datetime_from_string


def is_nat(value) -> bool:
    return value is pd.NaT


# --- Null / missing inputs ---

def test_nat_input_returns_nat():
    assert is_nat(datetime_from_string(pd.NaT))

def test_none_input_returns_nat():
    assert is_nat(datetime_from_string(None))

def test_float_nan_returns_nat():
    assert is_nat(datetime_from_string(float('nan')))

def test_numpy_nan_returns_nat():
    assert is_nat(datetime_from_string(np.nan))

def test_string_nan_returns_nat():
    assert is_nat(datetime_from_string('nan'))

def test_string_None_returns_nat():
    assert is_nat(datetime_from_string('None'))

def test_string_NaT_returns_nat():
    assert is_nat(datetime_from_string('NaT'))

def test_empty_string_returns_nat():
    assert is_nat(datetime_from_string(''))


# --- Already-datetime / already-date inputs ---

def test_datetime_passthrough():
    dt_in = datetime.datetime(2023, 1, 15, 10, 30, 0)
    assert datetime_from_string(dt_in) == dt_in

def test_datetime_with_tzinfo_passthrough():
    dt_in = datetime.datetime(2023, 1, 15, 10, 30, tzinfo=datetime.timezone.utc)
    assert datetime_from_string(dt_in) == dt_in

def test_date_converted_to_midnight_datetime():
    result = datetime_from_string(datetime.date(2023, 1, 15))
    assert isinstance(result, datetime.datetime)
    assert result == datetime.datetime(2023, 1, 15, 0, 0, 0)


# --- Integer epoch inputs ---

def test_int_epoch_nanoseconds():
    assert datetime_from_string(1372377600000000000) == datetime.datetime(2013, 6, 28, 0, 0, 0)

def test_int_epoch_milliseconds():
    assert datetime_from_string(1372809600000) == datetime.datetime(2013, 7, 3, 0, 0, 0)

def test_int_epoch_seconds():
    assert datetime_from_string(1373241600) == datetime.datetime(2013, 7, 8, 0, 0, 0)

def test_int_unrecognized_length_coerce():
    assert is_nat(datetime_from_string(12345, errors='coerce'))

def test_int_unrecognized_length_error():
    with pytest.raises(Exception):
        datetime_from_string(12345, errors='error')


# --- ISO 8601 strings ---

def test_iso8601_basic():
    assert datetime_from_string('2023-01-15T10:30:00') == datetime.datetime(2023, 1, 15, 10, 30, 0)

def test_iso8601_with_z():
    result = datetime_from_string('2023-01-15T10:30:00Z')
    assert result.replace(tzinfo=None) == datetime.datetime(2023, 1, 15, 10, 30, 0)
    assert result.utcoffset() == datetime.timedelta(0)

def test_iso8601_with_offset():
    result = datetime_from_string('2016-12-31T23:59:59+12:30')
    assert result.replace(tzinfo=None) == datetime.datetime(2016, 12, 31, 23, 59, 59)

def test_iso8601_hour_and_minute_only():
    assert datetime_from_string('2023-12-20T20:20') == datetime.datetime(2023, 12, 20, 20, 20, 0)

def test_iso8601_milliseconds_z():
    result = datetime_from_string('2021-05-10T09:05:12.000Z')
    assert result.replace(tzinfo=None) == datetime.datetime(2021, 5, 10, 9, 5, 12)

def test_iso8601_out_of_range_coerce():
    assert is_nat(datetime_from_string('3015-01-01T23:00:00Z', errors='coerce'))

def test_iso8601_out_of_range_error():
    with pytest.raises(Exception):
        datetime_from_string('3015-01-01T23:00:00Z', errors='error')


# --- Date with separator strings ---

def test_slash_separator_mdy():
    result = datetime_from_string('01/15/2023')
    assert result == datetime.datetime(2023, 1, 15, 0, 0, 0)

def test_dash_separator_ymd():
    result = datetime_from_string('2023-01-15')
    assert result == datetime.datetime(2023, 1, 15, 0, 0, 0)

def test_dot_separator_dmy():
    result = datetime_from_string('15.01.2023')
    assert result == datetime.datetime(2023, 1, 15, 0, 0, 0)


# --- Digit-only strings ---

def test_yyyymmdd_string():
    assert datetime_from_string('20230115') == datetime.datetime(2023, 1, 15, 0, 0, 0)

def test_yyyymm_string():
    assert datetime_from_string('202301') == datetime.datetime(2023, 1, 1, 0, 0, 0)


# --- Natural language / dateutil fallback ---

def test_natural_language_date():
    assert datetime_from_string('June 3, 2026') == datetime.datetime(2026, 6, 3, 0, 0, 0)


# --- errors parameter behavior ---

def test_invalid_string_coerce_returns_nat():
    assert is_nat(datetime_from_string('not_a_date_at_all_!!', errors='coerce'))

def test_invalid_string_error_raises():
    with pytest.raises(Exception):
        datetime_from_string('not_a_date_at_all_!!', errors='error')

def test_default_errors_is_coerce():
    assert is_nat(datetime_from_string('not_a_date_at_all_!!'))


# --- Existing test_dates from utils.py ---

def test_existing_test_dates():
    from morpc.utils import test_dates
    for d in test_dates:
        result = datetime_from_string(d, errors='coerce')
        assert result is not None
