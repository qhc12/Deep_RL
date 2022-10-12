from gym_simulator.utils.utils import increment_level, decrement_level


class RoadEvent:
    """
    Class for road events. Different road events (both Dynamic and Static) are all created with this class.
    """

    def __init__(self, name, event_type, start, end, max_level, max_speed):
        """
        name: the name of the event
        event_type: an enum specifying whether the event is dynamic or static
        start: the starting position of the event
        end: the ending position of the event
        max_level: the maximum automation level that is available during the event
        max_speed: the maximum speed that can be driven during the event
        """
        self.name = name
        self.event_type = event_type
        self.start = start
        self.end = end
        self.max_level = max_level  # Maximum available level when this event occurs
        self.pessimistic_max_level = decrement_level(max_level)  # One lower than the realistic max level for this event
        self.optimistic_max_level = increment_level(max_level)  # One higher than the realistic max level for this event
        self.max_speed = max_speed
