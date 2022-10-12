from gym_simulator.actions.emergency_stop import EmergencyStop
from gym_simulator.evaluation.abstract_safety_event import AbstractSafetyEvent
from gym_simulator.evaluation.safety_types import SafetyType


class UnnecessaryES(AbstractSafetyEvent):
    """
    Represents situation in which an unnecessary emergency stop is made.
    """

    def __init__(self, config, car, driver, last_action):
        super().__init__(config, car, SafetyType.UNCOMFORTABLE, UnnecessaryES.get_name())
        self.driver = driver
        self.last_action = last_action

    def is_active(self):
        active = isinstance(self.last_action, EmergencyStop) and \
                 ((self.car.current_level < "L3" and self.driver.ttdu > 5.0) or
                  (self.car.current_level > "L2" and self.driver.ttdf == 0))
        self.last_action = None
        return active

    @staticmethod
    def get_name():
        return "UnnecessaryES"
