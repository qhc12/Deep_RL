import importlib
import inspect
from os import listdir
from os.path import isfile, join


class RewardFactory:
    """
    Factory class for creation of Reward object.
    """

    def __init__(self, rl_settings):
        """
        Maps all the file names (excluding .py) to their corresponding classes, for easy automatic initialization
        of the reward class based on the settings.
        """
        self.rl_settings = rl_settings
        my_path = join("gym_simulator", "envs", "reward")
        self.reward_classes = {}
        base_loc = 'gym_simulator.envs.reward'
        for f in listdir(my_path):
            if isfile(join(my_path, f)) and not (f == "abstract_reward.py" or f == "reward_factory.py"):
                f = f[:-3]
                module = '{0}.{1}'.format(base_loc, f)
                for _, cls in inspect.getmembers(importlib.import_module(module), inspect.isclass):
                    if cls.__module__ == module:
                        self.reward_classes[f] = cls

    def get_reward_calculator(self, env):
        """
        Returns an instance of a reward class based on the RL settings.
        """
        return self.reward_classes[self.rl_settings.reward](env)
