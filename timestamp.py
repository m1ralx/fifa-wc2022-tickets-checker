from datetime import datetime


def get_timestamp(dt: datetime = None) -> int:
    dt = dt if dt is not None else datetime.now()
    return int(dt.timestamp() * 1000 * 1000)
