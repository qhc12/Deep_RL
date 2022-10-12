from abc import abstractmethod


class AbstractSafetyEvent:
    """
    Abstract class for any event that needs evaluation (see the directories in this directory). Any such event needs to
    inherit from this class.
    """

    def __init__(self, config, car, unsafety_type, name):
        """
        unsafety_type defines the type of event, which is an enum indicating the urgency of the situation.
        name defines a string with the name of the event.
        """
        self.config = config
        self.car = car
        self.type = unsafety_type
        self.name = name
        self.start = car.position
        self.end = car.position
        self.duration = 0.0
        self.is_pending = True

    def step(self):
        self.end = self.car.position
        self.is_pending = self.is_active()
        if not self.start == self.end:
            self.duration = self.duration + self.config.timestep

    @abstractmethod
    def is_active(self):
        pass
