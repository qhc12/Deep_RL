import os
import pickle

from globals import ROOT_DIR
from gym_simulator.config.preset_road import PresetRoad
import yaml


class RoadParser:
    """
    Class to parse a road file.
    """

    def __init__(self, road_file, include_route_data=False, route_data_file=None, custom_loc=False):
        # If custom_loc is True it means run configurations are used, and therefore the files should be taken from
        # there. Else, the files will be in the default directory defined below.
        if custom_loc:
            road_loc = road_file
            route_data_loc = route_data_file
        else:
            road_dir = os.path.join(ROOT_DIR, 'gym_simulator', 'config', 'predefined_road')
            road_loc = os.path.join(road_dir, road_file)
            route_data_loc = os.path.join(road_dir, route_data_file) if include_route_data else None

        with open(road_loc, 'r') as stream:
            try:
                self.road_map = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.route_data = None
        if include_route_data:
            with open(route_data_loc, 'rb') as f:
                self.route_data = pickle.load(f)

    def parse(self, config):
        """
        Create an object of the PresetRoad class from the parsed YAML files.
        """
        return PresetRoad(config, self.route_data, **self.road_map)
