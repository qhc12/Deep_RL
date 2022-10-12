from gym_simulator.actions.abstract_action import AbstractAction


class EnforceShiftLevel(AbstractAction):
    """
    This action enforces a switch to a different shift level.
    """

    def __init__(self, env, rng, enforced_level, position, remaining_time=None, latest_start=None):
        """
        Initializes enforcing a shift to a different automation level.
        remaining_time can be set to a custom value indicating how much time the driver has to get ready for the shift.
            When the remaining_time has counted down to 0, the shift is enforced. If not defined, remaining_time is set
            to the min_esl_time from driver preferences.
        """
        super().__init__(env.config, rng, position, latest_start)
        self.env = env
        self.enforced_level = enforced_level
        self.level_enforced = None
        self.remaining_time = remaining_time if remaining_time and remaining_time > 0 else self.config.min_esl_time

    def is_pending(self):
        return self.level_enforced is None

    def is_successful(self):
        return self.level_enforced

    def step(self, position):
        if not super().step(position):
            return
        # When the remaining_time is smaller than a single timestep, the level is enforced, such that it doesn't go
        # below 0.
        if self.remaining_time < self.config.timestep:
            self.level_enforced = True
        # Decrease the remaining_time by the time a single step takes.
        self.remaining_time -= self.config.timestep

    def end_action(self):
        self.level_enforced = True

    def resolve(self):
        if self.level_enforced:
            # Automation level is switched
            self.env.car.current_level = self.enforced_level
            self.env.switched = True

    def get_name(self):
        return "ES{0}".format(self.enforced_level)

    def __str__(self):
        return "ES{0} from {1} to {2}".format(self.enforced_level, self.start, self.end)

    def __repr__(self):
        return str(self)
