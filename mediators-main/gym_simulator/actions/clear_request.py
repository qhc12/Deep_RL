from gym_simulator.actions.abstract_action import AbstractAction
from gym_simulator.config.allowed_values import DriverEvent


class ClearRequest(AbstractAction):
    """
    This action clears a driver request.
    """

    def __init__(self, config, rng, driver, position):
        super().__init__(config, rng, position)
        self.driver = driver
        self.request_cleared = None

    def is_pending(self):
        return self.request_cleared is None

    def is_successful(self):
        return self.request_cleared

    def step(self, position):
        if not super().step(position):
            return

        # This action is always successful
        self.request_cleared = True

    def end_action(self):
        # This action is always successful
        self.request_cleared = True

    def resolve(self):
        if self.request_cleared:
            # Set the current driver request to None, since it is cleared
            self.driver.driver_request = None
            # End all driver request events
            self.driver.end_events(self.end, DriverEvent.DRIVER_REQUEST)

    def get_name(self):
        return "CR"
