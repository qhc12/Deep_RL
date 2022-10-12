from gym_simulator.actions.enforce_shift_level import EnforceShiftLevel
from gym_simulator.actions.suggest_shift_level import SuggestShiftLevel
from gym_simulator.evaluation.abstract_safety_event import AbstractSafetyEvent
from gym_simulator.evaluation.safety_types import SafetyType


class RecentSwitch(AbstractSafetyEvent):
    """
    Represents situation in which a Recent Switch is made, which happens when an action to shift levels is active
    shortly after a shift was already made.
    """

    def __init__(self, config, car, time_passed, time_of_last_switch, last_action):
        super().__init__(config, car, SafetyType.UNCOMFORTABLE, RecentSwitch.get_name())
        self.time_of_last_switch = time_of_last_switch
        self.time_passed = time_passed
        self.last_action = last_action

    def step(self):
        super().step()
        if not self.start == self.end:
            self.is_pending = False

    def is_active(self):
        new_ssl = isinstance(self.last_action, SuggestShiftLevel)
        new_esl = isinstance(self.last_action, EnforceShiftLevel)

        return (self.time_of_last_switch and (new_ssl or new_esl)
                and self.time_passed - self.time_of_last_switch < self.config.uncomfortable_switch)

    @staticmethod
    def get_name():
        return "RecentSwitch"
