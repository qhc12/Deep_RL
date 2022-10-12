from gym_simulator.actions.abstract_action import AbstractAction
from gym_simulator.utils.utils import calculate_probability_per_timestep, level_index


class SuggestShiftLevel(AbstractAction):
    """
    This action suggests a shift to a different automation level.
    """

    def __init__(self, env, rng, suggested_level, position, remaining_time=None, latest_start=None):
        """
        Initializes suggesting a shift to a different automation level.
        remaining_time can be set to a custom value indicating how much time the driver has to accept or reject the
            shift. When the remaining_time has counted down to 0, the action is terminated. If not defined,
            remaining_time is set to the comfortable_shift_time from driver preferences.
        """
        super().__init__(env.config, rng, position, latest_start)
        self.env = env
        self.suggested_level = suggested_level
        self.suggestion_accepted = None
        self.remaining_time = remaining_time if remaining_time else self.config.comfortable_shift_time
        total_timesteps = self.remaining_time / self.config.timestep
        # Boolean which is True when the driver has requested the level that is currently suggested
        level_requested = env.driver.driver_request is not None and env.driver.driver_request == suggested_level
        # The probability that a driver responds is different when the driver requested the shift
        response_probability = self.config.ss_resp_prob_dr if level_requested \
            else self.config.suggested_shift_response_probability
        # The probability that a driver accepts is also different when the driver requested the shift
        self.acceptance_probability = self.config.ss_acc_prob_dr if level_requested \
            else self.config.suggested_shift_acceptance_probability[level_index(self.suggested_level, True)]
        # Similar logic as for Correct Fatigue
        self.response_prob_per_timestep = calculate_probability_per_timestep(
            total_timesteps, response_probability)

    def is_pending(self):
        return self.suggestion_accepted is None

    def is_successful(self):
        return self.suggestion_accepted

    def step(self, position):
        if not super().step(position):
            return
        # There is a possibility that the driver does not respond (which is interpreted as a decline of the suggestion)
        if self.rng.rand() < self.response_prob_per_timestep:
            # If the driver responds, there is a predefined probability that he accepts the suggestion
            if self.rng.rand() < self.acceptance_probability:
                self.suggestion_accepted = True
            else:
                self.suggestion_accepted = False
        # There is a timeframe within which the driver needs to respond
        elif self.remaining_time < self.config.timestep:
            self.suggestion_accepted = False

        self.remaining_time -= self.config.timestep

    def end_action(self):
        if self.rng.rand() < self.acceptance_probability:
            self.suggestion_accepted = True
        else:
            self.suggestion_accepted = False

    def resolve(self):
        if self.suggestion_accepted:
            # The automation level is switched
            self.env.car.current_level = self.suggested_level
            self.env.switched = True
        else:
            # The decline of the driver is safed. This can be used in decision making (if the driver has just declined,
            # you don't want to suggest the same level again shortly after)
            self.env.driver.last_decline[self.suggested_level] = self.env.time_passed

    def get_name(self):
        return "SS{0}".format(self.suggested_level)

    def __str__(self):
        return "SS{0} from {1} to {2} was {3}accepted".format(self.suggested_level, self.start, self.end,
                                                              ("" if self.suggestion_accepted else "NOT "))

    def __repr__(self):
        return str(self)
