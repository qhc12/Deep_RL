from abc import ABC, abstractmethod


class Mediator(ABC):
    """
    Abstract class from which other mediator classes should inherit.
    """

    def __init__(self, log, noise, tta_levels):
        self.log = log
        self.noise = noise
        self.tta_levels = tta_levels

    @abstractmethod
    def get_action(self, env):
        """
        Returns the action suggested by the mediator system in the current step.
        """
        pass

    @abstractmethod
    def is_random(self):
        """
        Returns true if the MEDIATOR should return random actions.
        """
        pass

    @abstractmethod
    def set_future_action(self, env):
        """
        Calculates an action ahead of time, predicting future MEDIATOR behaviour.
        """
        pass
