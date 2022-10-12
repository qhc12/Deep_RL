import importlib
import inspect
from os import listdir
from os.path import join, isfile

from gym_simulator.envs.observations.obs_factory import ObservationFactory


class ObservationManager:
    """
    Class to manage the observation space and the variables in it.
    """

    def __init__(self, rl_settings):
        """
        rl_settings contains the type of observation space (see obs_factory.py for current options) and the observation
        variables that should be used (which can be any class in the variables directory that inherits from the abstract
        observation variables class). This constructor initializes the classes for the observation space and variables
        based on these settings.
        """
        self.rl_settings = rl_settings
        self.obs_variables = None  # Will hold the class for the observation variables

        # Code below automatically initializes the class based on the settings
        my_path = join("gym_simulator", "envs", "observations", "variables")
        base_loc = 'gym_simulator.envs.observations.variables'
        for f in listdir(my_path):
            if isfile(join(my_path, f)) and f == "{0}.py".format(self.rl_settings.obs_variables):
                f = f[:-3]
                module = '{0}.{1}'.format(base_loc, f)
                for _, cls in inspect.getmembers(importlib.import_module(module), inspect.isclass):
                    if cls.__module__ == module:
                        self.obs_variables = cls()
                break

        # Contains the class for the observation space
        self.obs_space_class = ObservationFactory.create_observation_class(rl_settings,
                                                                           self.obs_variables.init_obs_bounds())

    def get_observation_space(self):
        """
        Returns an instance of an OpenAI Gym Space. The instance returned depends on the rl settings.
        """
        return self.obs_space_class.define_observation_space()

    def get_observations(self, env):
        """
        Returns an array of observations that can be used in the OpenAI Gym Space.
        """
        return self.obs_space_class.get_observation(
            self.obs_space_class.transform(self.obs_variables.get_obs_dict(env)))
