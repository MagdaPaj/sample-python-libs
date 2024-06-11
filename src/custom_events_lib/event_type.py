from enum import Enum


class EventType(Enum):
    EXCEPTION = "Exception"
    MISSING_DATA = "MissingData"
    INVALID_DATA = "InvalidData"
