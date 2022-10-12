import os

import yaml

from globals import ROOT_DIR
from reinforcement_learning.rl_settings import RLSettings


class RLSettingsParser:
    """
    Class to parse RL Settings.
    """

    def __init__(self, rl_settings_file, custom_loc):
        if custom_loc:
            settings_loc = rl_settings_file
        else:
            settings_loc = os.path.join(ROOT_DIR, 'reinforcement_learning', 'settings', rl_settings_file)

        with open(settings_loc, 'r') as stream:
            try:
                self.settings_map = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def parse(self):
        return RLSettings(**self.settings_map)
