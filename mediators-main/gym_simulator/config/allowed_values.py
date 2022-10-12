from enum import Enum


class RoadEventType(Enum):
    """
    A road event type can either be static or dynamic.
    """
    STATIC, DYNAMIC = range(2)


class DriverEvent(Enum):
    """
    Enum for driver events. Each event has its own value. When a new event is created, it should also get its own
    enum here.
    """
    FATIGUE, DISTRACTION, NDRT, DRIVER_REQUEST = range(4)
