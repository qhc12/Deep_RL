import numpy as np

from gym_simulator.envs.observations.spaces.abstract_observation_space import AbstractObservationSpace
from gym import spaces


class DiscreteObservationSpace(AbstractObservationSpace):
    """
    A class to create and use a MultiDiscrete OpenAI Gym Space.
    """

    def define_observation_space(self):
        ranges = []
        for i, (key, value) in enumerate(self.obs_bounds_dict.items()):
            ranges.append(value[1] - value[0] + 1)
            self.obs_var_index[key] = i

        return spaces.MultiDiscrete(np.array(ranges, dtype=np.int64))

    def get_observation(self, obs_dict):
        """
        obs_dict is a dictionary mapping variable names to values. Each value should be within its predefined bound.

        Returns an array of all the values in the dictionary, mapped to 64-bit integers.
        """
        return super().build_obs(obs_dict, np.int64)
