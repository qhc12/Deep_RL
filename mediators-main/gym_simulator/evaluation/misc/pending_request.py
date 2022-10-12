from gym_simulator.evaluation.abstract_safety_event import AbstractSafetyEvent
from gym_simulator.evaluation.safety_types import SafetyType


class PendingRequest(AbstractSafetyEvent):
    """
    Represents situation in which the a driver request is pending.
    """

    def __init__(self, config, car, driver):
        super().__init__(config, car, SafetyType.MISC, PendingRequest.get_name())
        self.driver = driver

    def is_active(self):
        return self.driver.driver_request is not None and not self.car.current_level == self.driver.driver_request

    @staticmethod
    def get_name():
        return "PendingRequest"
