from gym_simulator.actions.abstract_action import AbstractAction
from gym_simulator.config.allowed_values import DriverEvent
from gym_simulator.utils.utils import calculate_gaussian_distribution


class CorrectDistraction(AbstractAction):
    """
    This action attempts to correct a distraction.
    """

    def __init__(self, config, rng, driver, position):
        super().__init__(config, rng, position)
        self.driver = driver
        self.corrected_distraction = None  # Boolean that is set to true when the distraction is successfully resolved
        mu, sigma = calculate_gaussian_distribution(self.config.timestep, self.config.max_cd_time,
                                                    self.config.cd_success_probability, -0.5)
        # The probability that the time of success lies between self.config.timestep and self.config.max_cd_time is
        # equal to self.config.cd_success_probability. If time_of_success lies outside this range, the CD action is
        # considered unsuccessful.
        time_of_success = self.rng.normal(mu, sigma)
        self.successful_timestep = None
        if self.config.timestep <= time_of_success <= self.config.max_cd_time:
            self.successful_timestep = round(time_of_success / self.config.timestep)

    def is_pending(self):
        return self.corrected_distraction is None

    def is_successful(self):
        return self.corrected_distraction

    def step(self, position):
        if not super().step(position):
            return

        # If the distraction of the driver is already 0, it can also not be corrected.
        if self.driver.distraction == 0:
            self.corrected_distraction = False
        # If the number of steps taken equals the successful_timestep calculated in the constructor, the distraction
        # is successfully corrected
        elif self.successful_timestep is not None and self.successful_timestep == self.steps_taken:
            self.corrected_distraction = True
        # The max_cd_time has been exceeded and therefore the distraction is not corrected
        elif self.time_passed >= self.config.max_cd_time:
            self.corrected_distraction = False

    def end_action(self):
        # Simple logic to decide whether Correct Distraction is successful, only used for instant actions
        if self.rng.rand() < self.config.cd_success_probability:
            self.corrected_distraction = True
        else:
            self.corrected_distraction = False

    def resolve(self):
        if self.corrected_distraction:
            # If the distraction has been successfully corrected, it means distraction level goes back to 0.
            self.driver.distraction = 0
            # This value is set to True such that TTDU is updated
            self.driver.update_distraction = True
            # This ends any distraction event that was pending
            self.driver.end_events(self.end, DriverEvent.DISTRACTION)

    def get_name(self):
        return "CD"
