from abc import ABC, abstractmethod


class AbstractObservationVariables(ABC):
    """
    A class that defines observation variables should inherit from this class and implement its abstract methods.
    """

    @abstractmethod
    def init_obs_bounds(self):
        """
        Return a dictionary that maps variables names to pairs of lower and upper bounds for this variable.
        """
        pass

    @abstractmethod
    def get_obs_dict(self, env):
        """
        Return a dictionary that maps variables names to their current value. These values should be within the bounds
        defined for the respective variable.
        """
        pass
