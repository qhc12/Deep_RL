from enum import Enum


class SafetyType(Enum):
    """
    Enum defining different levels of urgency for safety events.
    """
    MISC, UNCOMFORTABLE, CRITICAL = range(3)
