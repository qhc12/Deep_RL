from gym_simulator.config.config import Config
from globals import ROOT_DIR
import yaml
import os


class ConfigParser:
    """
    Class to parse a config file that is located in config_files directory. Also, the TTDU and TTDF values are
    parsed, and the view file.
    """

    def __init__(self, config_file, view_file="view.yaml", custom_loc=False):
        config_dir = os.path.join(ROOT_DIR, 'gym_simulator', 'config')
        # If custom_loc is True it means run configurations are used, and therefore the files should be taken from
        # there. Else, the files will be in the default directory defined above.
        if custom_loc:
            config_loc = config_file
            view_loc = view_file
        else:
            config_loc = os.path.join(config_dir, 'config_files', config_file)
            view_loc = os.path.join(config_dir, 'view', view_file)

        with open(config_loc, 'r') as stream:
            try:
                self.config_map = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        with open(os.path.join(config_dir, 'ttd_values', 'ttd.yaml'), 'r') as stream:
            try:
                self.config_map.update(yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)

        with open(view_loc, 'r') as stream:
            try:
                self.config_map.update(yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)

    def parse(self):
        """
        Create an object of the Config class from the parsed YAML files.
        """
        return Config(**self.config_map)
