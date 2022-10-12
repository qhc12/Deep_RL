from gym_simulator.config.allowed_values import DriverEvent
from gym_simulator.events.driver_events.distraction import Distraction
from gym_simulator.events.driver_events.driver_request import DriverRequest
from gym_simulator.events.driver_events.fatigue import Fatigue
from gym_simulator.events.driver_events.ndrt import NDRT


def map_driver_event_to_class(dre):
    """
    Maps a DriverEvent enum to its corresponding event class.
    """
    if dre == DriverEvent.DRIVER_REQUEST:
        return DriverRequest
    elif dre == DriverEvent.FATIGUE:
        return Fatigue
    elif dre == DriverEvent.DISTRACTION:
        return Distraction
    elif dre == DriverEvent.NDRT:
        return NDRT
