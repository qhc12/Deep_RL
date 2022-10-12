import os
import yaml
from globals import ROOT_DIR
from mediator_system.preferences.driver_preferences import Preferences


class PreferencesParser:
    """
    Class to parse preferences file for the MediatorInterface system.
    """

    def __init__(self, filename, custom_loc=False):
        if custom_loc:
            preference_dir = filename
        else:
            preference_dir = os.path.join(ROOT_DIR, 'mediator_system', 'preferences', 'driver_profiles', filename)

        with open(preference_dir, 'r') as stream:
            try:
                self.preferences_map = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def parse(self):
        """
        Create an object of the Preferences class from the parsed YAML file.
        """
        return Preferences(**self.preferences_map)
