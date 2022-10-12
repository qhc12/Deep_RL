from gym_simulator.config.allowed_values import DriverEvent
from gym_simulator.events.driver_events.abstract_driver_event import AbstractDriverEvent


class Fatigue(AbstractDriverEvent):
    """
    Class for Fatigue event.
    """

    def __init__(self, config, rng, starting_position):
        super().__init__(config, rng, starting_position)

    def step(self, driver, car):
        if not self.is_pending:
            return
        self.end = car.position
        # For the visualization, the fatigue event cannot end at the same timestep it starts, so it ends one timestep
        # later
        if self.start == self.end:
            return
        if driver.fatigue < 4:
            driver.fatigue = driver.fatigue + 1
        driver.update_fatigue = True
        self.is_pending = False

    def is_possible(self, current_level):
        return True

    def get_enum(self):
        return DriverEvent.FATIGUE
