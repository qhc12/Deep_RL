from gym_simulator.envs.observations.spaces.continuous_observation_space import ContinuousObservationSpace
from gym_simulator.envs.observations.spaces.discrete_observation_space import DiscreteObservationSpace


class ObservationFactory:

    @staticmethod
    def create_observation_class(rl_settings, obs_dict):
        """
        Create the correct instance of a class for observation space based on the settings.

        obs_dict is a dictionary that maps variable names to lower and upper bounds.
        """
        if rl_settings is None or rl_settings.obs_space == "discrete":
            return DiscreteObservationSpace(obs_dict)
        elif rl_settings.obs_space == "continuous":
            return ContinuousObservationSpace(obs_dict)
        else:
            raise Exception("{0} observation space has not yet been implemented.".format(rl_settings.obs_space))
