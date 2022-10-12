from abc import ABC, abstractmethod


class AbstractDriverEvent(ABC):
    """
    Abstraction for driver event. Every driver event class should inherit from this.

    When creating a new driver event, an enum needs to be added for this event in gym_simulator/config/allowed_values.py
    and its mapping needs to be added in the function "map_driver_events" in gym_simulator/config/config.py. Finally,
    a mapping from Enum to class should be added in gym_simulator/config/enums_to_classes_mapping.py
    """

    def __init__(self, config, rng, starting_position):
        self.config = config
        self.rng = rng
        self.start = starting_position  # The position of the car when the event starts
        self.end = starting_position  # The position of the car when the event ends
        self.is_pending = True

    @abstractmethod
    def step(self, driver, car):
        """
        Takes a step in the driver event and possibly updates properties of driver and/or car.
        """
        pass

    @abstractmethod
    def is_possible(self, current_level):
        """
        Returns True if the event can happen given the current automation level.
        """
        pass

    @abstractmethod
    def get_enum(self):
        """
        Returns an Enum of the driver event.
        """
        pass
