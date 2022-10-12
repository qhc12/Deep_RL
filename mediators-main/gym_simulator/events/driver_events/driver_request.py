from gym_simulator.config.allowed_values import DriverEvent
from gym_simulator.events.driver_events.abstract_driver_event import AbstractDriverEvent


class DriverRequest(AbstractDriverEvent):
    """
    Class for Driver Request event.
    """

    def __init__(self, config, rng, starting_position):
        super().__init__(config, rng, starting_position)
        # The level requested by the driver
        self.requested_level = self.rng.choice([level for level in ["L0", "L2", "L3", "L4"]
                                                if level <= self.config.maximum_automation_level])
        self.changed = False  # Indicates whether the request has already been assigned to the driver

    def step(self, driver, car):
        if not self.is_pending:
            return
        self.end = car.position
        if not self.changed:
            driver.driver_request = self.requested_level
            self.changed = True
        # Small probability that a driver cancels a request by itself
        elif self.rng.rand() < self.config.driver_request_cancel_prob:
            driver.driver_request = None
            self.is_pending = False

    def is_possible(self, current_level):
        return not self.requested_level == current_level

    def get_enum(self):
        return DriverEvent.DRIVER_REQUEST

