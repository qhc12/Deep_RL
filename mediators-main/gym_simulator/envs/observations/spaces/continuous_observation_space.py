import numpy as np

from gym_simulator.envs.observations.spaces.abstract_observation_space import AbstractObservationSpace
from gym import spaces


class ContinuousObservationSpace(AbstractObservationSpace):
    """
    A class to create and use a Box OpenAI Gym Space, which is a continous space.
    """

    def define_observation_space(self):
        lower_bounds = []
        upper_bounds = []
        for i, (key, value) in enumerate(self.obs_bounds_dict.items()):
            lower_bounds.append(value[0])
            upper_bounds.append(value[1])
            self.obs_var_index[key] = i

        return spaces.Box(low=np.array(lower_bounds), high=np.array(upper_bounds), dtype=np.float32)

    def get_observation(self, obs_dict):
        """
        obs_dict is a dictionary mapping variable names to values. Each value should be within its predefined bound.

        Returns an array of all the values in the dictionary, mapped to 32-bit floats.
        """
        return super().build_obs(obs_dict, np.float32)
