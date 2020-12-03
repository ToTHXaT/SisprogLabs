from typing import *


def to_int(s: str) -> int:
    try:
        return int(s, 0)
    except ValueError:
        return int(s)


def to_int_safe(s: str) -> Optional[int]:
    try:
        return to_int(s)
    except ValueError:
        return None
