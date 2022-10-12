from gym_simulator.actions.enforce_shift_level import EnforceShiftLevel
from gym_simulator.evaluation.abstract_safety_event import AbstractSafetyEvent
from gym_simulator.evaluation.safety_types import SafetyType


class QuickTakeover(AbstractSafetyEvent):
    """
    Represents situation in which the a quick takeover needs to be made, which happens when a driver needs to take
    over control of the vehicle in a very short timeframe.
    """

    def __init__(self, config, car, resolved_action):
        super().__init__(config, car, SafetyType.UNCOMFORTABLE, QuickTakeover.get_name())
        self.resolved_action = resolved_action

    def step(self):
        super().step()
        if not self.start == self.end:
            self.is_pending = False

    def is_active(self):
        resolved_esl = isinstance(self.resolved_action, EnforceShiftLevel)
        return resolved_esl and self.resolved_action.level_enforced and \
            self.resolved_action.time_passed < self.config.comfortable_shift_time

    @staticmethod
    def get_name():
        return "QuickTakeover"
