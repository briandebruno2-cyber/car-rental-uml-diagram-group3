"""Small helper used by every class to create readable IDs such as VEH-001."""
from itertools import count

_counters = {}


def next_id(prefix):
    counter = _counters.setdefault(prefix, count(1))
    return f"{prefix}-{next(counter):03d}"
