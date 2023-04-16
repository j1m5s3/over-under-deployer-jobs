from typing import Dict
from datetime import datetime, timedelta


def get_iso_range_from_now(num_hours: int) -> Dict:
    """
    Get ISO range from now
    :param num_hours:
    :return: {'end_iso': end_iso, 'start_iso': start_iso}
    """
    end = datetime.now()
    start = end - timedelta(hours=num_hours)

    end_timestamp = int(end.timestamp())
    start_timestamp = int(start.timestamp())

    end_iso = datetime.fromtimestamp(end_timestamp).isoformat()
    start_iso = datetime.fromtimestamp(start_timestamp).isoformat()

    return {'end_iso': end_iso, 'start_iso': start_iso}


def convert_iso_to_timestamp(iso_string: str) -> int:
    """
    Convert ISO string to timestamp
    :param iso_string:
    :return: timestamp
    """
    if "Z" in iso_string:
        iso_string = iso_string[:-9]
    dt = datetime.fromisoformat(iso_string)

    return dt.timestamp()


def convert_timestamp_to_iso(timestamp):
    """
    Convert timestamp to ISO string
    :param timestamp:
    :return: ISO string
    """
    dt = datetime.fromtimestamp(timestamp)

    return dt.isoformat()


def get_timedelta_from_timestamps(start_timestamp, end_timestamp):
    """
    Get timedelta from timestamps
    :param start_timestamp:
    :param end_timestamp:
    :return: timedelta
    """
    start = datetime.fromtimestamp(start_timestamp)
    end = datetime.fromtimestamp(end_timestamp)

    return (end - start).total_seconds()
