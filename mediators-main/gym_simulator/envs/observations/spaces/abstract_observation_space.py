from abc import ABC, abstractmethod

import numpy as np


class AbstractObservationSpace(ABC):
    """
    Abstract class for an observation space. When defining a new observation space, it should be a class that inherits
    from this class and implements its abstract methods.

    The class contains some methods for transforming
    """

    def __init__(self, obs_bounds_dict):
        """
        Initialize the observation space with a dictionary containing lower and upper bounds for all variables.
        """
        self.obs_bounds_dict = obs_bounds_dict
        # Dictionary that will hold a mapping of variable names to indices in the resulting observation space array
        # Can be used to transform the array back to a dictionary
        self.obs_var_index = {}

    @abstractmethod
    def define_observation_space(self):
        """
        Returns an instances of an OpenAI Gym space, with specific bounds based on the bounds defined in the variable
        class.
        """
        pass

    @abstractmethod
    def get_observation(self, obs):
        pass

    def build_obs(self, obs_dict, dtype):
        """
        Function to build an array containing observations that can be used in OpenAI Gym.

        obs_dict is a dictionary mapping variables to values, where all values should be within bounds defined in the
            observation variables class that is used.
        dtype defines the type of number to use, values are automatically cast to this type.

        Returns an array with a value for each key in the dictionary.
        """
        values = np.empty(len(obs_dict.keys()), dtype=dtype)
        for key, value in obs_dict.items():
            # The values are inserted at the index that is previously used for this variable, such that the array
            # can be mapped back to a dictionary later on
            i = self.obs_var_index[key]
            values[i] = value
        return values

    def transform(self, obs_dict):
        """
        Takes a dictionary of variables mapping to values (defining observations) and transforms some values such that
        they can be used in the OpenAI Gym spaces. Function may need to be extended depending on the variables
        used.

        Returns a dictionary with same keys, and possibly different values.
        """
        # Transform level string (L0/L2/L3/L4) to integer (0/1/2/3 respectively)
        obs_dict["current_level"] = self._transform_current_level(obs_dict["current_level"])
        return obs_dict

    def reverse_transform(self, obs_arr):
        """
        obs_arr is an array containing observations.

        This function converts the array back to a dictionary mapping variable names to values. This can be useful for
        printing purposes.
        """
        obs_dict = {}
        for key, i in self.obs_var_index.items():
            val = obs_arr[i]
            if key == "current_level" or key == "max_level":
                obs_dict[key] = self._transform_current_level(val, True)
            elif key == "ssl4_declined":
                obs_dict[key] = bool(val)
            else:
                obs_dict[key] = val
        return obs_dict

    def _transform_current_level(self, val, reverse=False):
        """
        Transforms current level to index, or index to current level (if reverse = True).
        So val can be either an index or a level.
        """
        levels = ["L0", "L2", "L3", "L4"]
        if reverse:
            return levels[int(val)]
        return next(i for i, level in enumerate(levels) if level == val)
