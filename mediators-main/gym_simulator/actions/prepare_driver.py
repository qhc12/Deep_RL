from gym_simulator.actions.abstract_action import AbstractAction
from gym_simulator.config.allowed_values import DriverEvent
from gym_simulator.utils.utils import calculate_gaussian_distribution


class PrepareDriver(AbstractAction):
    """
    Prepares the driver to take over control.
    """

    def __init__(self, config, rng, driver, position):
        super().__init__(config, rng, position)
        self.driver = driver
        # Prepare driver aims to correct NDRT (a special type of distraction that is used to describe the driver being
        # absent while driving in L3 or L4. TTDF is the estimated time it takes to prepare the driver and is based on
        # the NDRT level.
        self.ttdf = self.config.ttdf['ndrt'][self.driver.ndrt]
        self.corrected_ndrt = None
        self.successful_timestep = None
        if self.ttdf > 0:
            # The logic below is the same as in correct distraction.
            mu, sigma = calculate_gaussian_distribution(self.config.timestep, self.ttdf,
                                                        self.config.pd_success_probability, 1.0)
            time_of_success = self.rng.normal(mu, sigma)
            if self.config.timestep <= time_of_success <= self.ttdf:
                self.successful_timestep = round(time_of_success / self.config.timestep)

    def is_pending(self):
        return self.corrected_ndrt is None

    def is_successful(self):
        return self.corrected_ndrt

    def step(self, position):
        if not super().step(position):
            return

        # If NDRT is 0, there is nothing to be prepared
        if self.driver.ndrt == 0:
            self.corrected_ndrt = False
        elif self.successful_timestep is not None and self.successful_timestep == self.steps_taken:
            self.corrected_ndrt = True
        elif self.time_passed >= self.ttdf:
            self.corrected_ndrt = False

    def end_action(self):
        if self.rng.rand() < self.config.pd_success_probability:
            self.corrected_ndrt = True
        else:
            self.corrected_ndrt = False

    def resolve(self):
        if self.corrected_ndrt:
            self.driver.ndrt = 0
            self.driver.end_events(self.end, DriverEvent.NDRT)

    def get_name(self):
        return "PD"
