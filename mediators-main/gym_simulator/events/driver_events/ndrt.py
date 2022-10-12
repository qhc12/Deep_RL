from gym_simulator.config.allowed_values import DriverEvent
from gym_simulator.events.driver_events.abstract_driver_event import AbstractDriverEvent


class NDRT(AbstractDriverEvent):
    """
    Class for NDRT event, which is a distraction event that happens when driving in L3/L4.
    """

    def __init__(self, config, rng, starting_position):
        super().__init__(config, rng, starting_position)
        self.changed = False  # Indicates if NDRT has been started

    def step(self, driver, car):
        if not self.is_pending:
            return
        self.end = car.position
        if not self.changed:
            driver.ndrt = self.rng.randint(1, 4)  # Set the NDRT level randomly
            self.changed = True
        elif self.rng.rand() < self.config.ndrt_ends_prob:
            driver.ndrt = 0
            self.is_pending = False

    def is_possible(self, current_level):
        return current_level >= "L3"

    def get_enum(self):
        return DriverEvent.NDRT
