from gym_simulator.evaluation.abstract_safety_event import AbstractSafetyEvent
from gym_simulator.evaluation.safety_types import SafetyType


class DriverUnfit(AbstractSafetyEvent):
    """
    Represents situation in which the Driver is unfit, which happens when the current automation level is lower than L3
    and the TTDU == 0.
    """

    def __init__(self, config, car, driver):
        super().__init__(config, car, SafetyType.CRITICAL, DriverUnfit.get_name())
        self.driver = driver

    def is_active(self):
        return self.car.current_level < "L3" and self.driver.ttdu == 0

    @staticmethod
    def get_name():
        return "DriverUnfit"
