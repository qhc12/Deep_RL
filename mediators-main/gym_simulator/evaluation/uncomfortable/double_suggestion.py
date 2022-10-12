from gym_simulator.actions.suggest_shift_level import SuggestShiftLevel
from gym_simulator.evaluation.abstract_safety_event import AbstractSafetyEvent
from gym_simulator.evaluation.safety_types import SafetyType


class DoubleSuggestion(AbstractSafetyEvent):
    """
    Represents situation in which the a double suggestion is made, which happens when a shift to a level is suggested
    twice in a short timeframe.
    """

    def __init__(self, config, car, driver, time_passed, last_action):
        super().__init__(config, car, SafetyType.UNCOMFORTABLE, DoubleSuggestion.get_name())
        self.driver = driver
        self.time_passed = time_passed
        self.last_action = last_action

    def step(self):
        super().step()
        if not self.start == self.end:
            self.is_pending = False

    def is_active(self):
        new_ssl = isinstance(self.last_action, SuggestShiftLevel)
        last_decline = None
        if new_ssl:
            suggested_level = self.last_action.suggested_level
            last_decline = self.driver.last_decline[suggested_level]

        return new_ssl and last_decline and self.time_passed - last_decline < self.config.decline_threshold

    @staticmethod
    def get_name():
        return "DoubleSuggestion"
