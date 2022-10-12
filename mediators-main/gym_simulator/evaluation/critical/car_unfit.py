from gym_simulator.evaluation.abstract_safety_event import AbstractSafetyEvent
from gym_simulator.evaluation.safety_types import SafetyType


class CarUnfit(AbstractSafetyEvent):
    """
    Represents situation in which the Car is unfit, which happens when its current automation level is higher than
    the maximum available automation level.
    """

    def __init__(self, config, car):
        super().__init__(config, car, SafetyType.CRITICAL, CarUnfit.get_name())

    def is_active(self):
        return self.car.current_level > self.car.road.current_max_level

    @staticmethod
    def get_name():
        return "CarUnfit"
