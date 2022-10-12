import os
from abc import ABC, abstractmethod

import yaml

from globals import ROOT_DIR


class AbstractTrainer(ABC):
    """
    Abstract class for RL Trainers, from which each trainer should inherit.
    """

    def __init__(self, settings, method):
        self.method = method
        self.save_dir = os.path.join(ROOT_DIR, "RL_models", self.method.__name__, settings.save_as)
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)
        self.save_path = os.path.join(self.save_dir, "trained_model")
        self.timesteps = settings.timesteps

        self.env_args = {
            "config_file": settings.config_file,
            "driver_preferences_file": settings.driver_profile,
            "view_file": settings.view_file,
            "road_file": settings.get("road_file", None),
            "render": False,
            "rl_settings_file": settings.rl_settings_file
        }

    @abstractmethod
    def learn(self):
        """
        Train a RL model.
        """
        pass

    @abstractmethod
    def get_model(self):
        """
        Return the RL model used.
        """
        pass

    @abstractmethod
    def get_rl_settings(self):
        """
        Return the RL settings used.
        """
        pass

    def save(self):
        """
        Save a trained model.
        """
        self.get_model().save(self.save_path)
        with open(os.path.join(self.save_dir, "rl_settings.yaml"), 'w', newline='', encoding='utf-8') as f:
            yaml.dump(self.get_rl_settings().__dict__, f, default_flow_style=False, sort_keys=False)

    def train(self):
        """
        Train and save a RL model.
        """
        self.learn()
        self.save()
