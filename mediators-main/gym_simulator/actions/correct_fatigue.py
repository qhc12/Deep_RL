from gym_simulator.actions.abstract_action import AbstractAction
from gym_simulator.utils.utils import calculate_probability_per_timestep


class CorrectFatigue(AbstractAction):
    """
    This action attempts to correct fatigue.
    """

    def __init__(self, config, rng, driver, position):
        super().__init__(config, rng, position)
        self.driver = driver
        self.corrected_fatigue = None
        # The success_prob_per_timestep is calculated in such a way, that the cumulative probability of the action
        # being successful within self.config.max_correct_fatigue_time is equal to self.config.cf_success_probability
        total_timesteps = self.config.max_correct_fatigue_time / self.config.timestep
        self.success_prob_per_timestep = calculate_probability_per_timestep(total_timesteps,
                                                                            self.config.cf_success_probability)

    def is_pending(self):
        return self.corrected_fatigue is None

    def is_successful(self):
        return self.corrected_fatigue

    def step(self, position):
        if not super().step(position):
            return
        # If the driver has uncorrectable fatigue, it means an earlier attempt was made to correct fatigue, which
        # failed. This indicates fatigue is not task related and therefore not correctable. So the action fails
        # instantly.
        if self.driver.uncorrectable_fatigue or self.driver.fatigue == 0:
            self.corrected_fatigue = False
        elif self.rng.rand() < self.success_prob_per_timestep:
            self.corrected_fatigue = True
        # Time limit for this action exceeded, thus unsuccessful
        elif self.time_passed >= self.config.max_correct_fatigue_time:
            self.corrected_fatigue = False

    def end_action(self):
        if self.rng.rand() < self.config.cf_success_probability:
            self.corrected_fatigue = True
        else:
            self.corrected_fatigue = False

    def resolve(self):
        if self.corrected_fatigue:
            self.driver.uncorrectable_fatigue = False
            # Contrary to distraction, fatigue level only decreases by 1 when CF is successful
            self.driver.fatigue = self.driver.fatigue - 1
            # Set to true to update TTDU
            self.driver.update_fatigue = True
        elif self.driver.fatigue > 0:
            # The action was not able to correct fatigue, thus fatigue is uncorrectable
            self.driver.uncorrectable_fatigue = True

    def get_name(self):
        return "CF"
