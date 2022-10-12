from abc import ABC, abstractmethod


class AbstractReward(ABC):
    """
    Abstract reward class. Any reward class needs to inherit this class and implement its abstract method.
    """

    def __init__(self, env):
        self.env = env

    @abstractmethod
    def get_reward(self):
        """
        Returns a reward based on the current state of the environment.
        """
        pass
