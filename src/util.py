import time

import settings


def filter_batch_names(start_date, end_date, batch_names):
    end_date_str = end_date.strftime("%Y%m%d")
    start_date_str = start_date.strftime("%Y%m%d")

    batch_names = [b for b in batch_names if start_date_str <= b <= end_date_str]
    return batch_names


def parse_date_string(s):
    """Parse date string in YYYYMMDD format"""
    year, month, day = time.strptime(s, '%Y%m%d')[:3]
    return year, month, day


def is_batch_name(batch_name, include_empty):
    """
    Check whether backed-up file name matches expectation

    Note, accepted batch_names are either 'Leeg' or dates in YYYYMMDD format.
    """
    if include_empty and batch_name == settings.NPR_NULL_VALUE:
        return True

    try:
        parse_date_string(batch_name)
    except:
        return False
    else:
        return True


def validate_batch_names(batch_names, include_empty):
    """Filter list of potential batch names, accept only valid ones"""
    return [bn for bn in batch_names if is_batch_name(bn, include_empty)]


def str_to_bool(boolstr):
    if not isinstance(boolstr, str):
        return False
    return boolstr.lower() in ('1', 't', 'true')
