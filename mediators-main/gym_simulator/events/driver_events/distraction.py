from gym_simulator.config.allowed_values import DriverEvent
from gym_simulator.events.driver_events.abstract_driver_event import AbstractDriverEvent


class Distraction(AbstractDriverEvent):
    """
    Class for Distraction event.
    """

    def __init__(self, config, rng, starting_position):
        super().__init__(config, rng, starting_position)
        self.increased = False  # True as soon as the distraction increased once

    def step(self, driver, car):
        if not self.is_pending:
            return
        self.end = car.position
        # If distraction level has not increased yet (and is able to), increase it by 1
        if not self.increased and driver.distraction < 3:
            driver.distraction = driver.distraction + 1
            driver.update_distraction = True
            self.increased = True
        # Distraction is not at its max level yet, so there's a chance that it increases
        elif driver.distraction < 3:
            rand_no = self.rng.rand()
            # Probability that distraction increases
            if rand_no < self.config.distraction_increase_prob ** driver.distraction:
                driver.distraction = driver.distraction + 1
                driver.update_distraction = True
            # Probability that distraction ends midway
            elif rand_no > (1 - self.config.distraction_ends_midway_prob):
                driver.distraction = 0
                driver.update_distraction = True
                self.is_pending = False
        # Probability that distraction ends when it is at maximum level
        elif self.rng.rand() < self.config.distractions_ends_prob:
            driver.distraction = 0
            driver.update_distraction = True
            self.is_pending = False

    def is_possible(self, current_level):
        return current_level < 'L3'

    def get_enum(self):
        return DriverEvent.DISTRACTION
