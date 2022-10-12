from gym_simulator.actions.abstract_action import AbstractAction


class EmergencyStop(AbstractAction):
    """
    This action makes an Emergency Stop (and thereby terminates the simulation).
    """

    def __init__(self, env, rng):
        super().__init__(env.config, rng, env.car.position)
        self.env = env
        self.has_stopped = None

    def is_pending(self):
        return self.has_stopped is None

    def is_successful(self):
        # This action is always successful
        return True

    def step(self, position):
        if not super().step(position):
            return
        # The action always stops after 1 timestep
        self.has_stopped = True

    def end_action(self):
        self.has_stopped = True

    def resolve(self):
        if self.has_stopped:
            # This terminates the simulation
            self.env.done = True
            self.env.evaluation.made_es = True

    def get_name(self):
        return "ES"
