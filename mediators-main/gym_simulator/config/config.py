# Don't remove this import, it's used for parsing some of the YAML files
import sys

from gym_simulator.config.allowed_values import *


def map_driver_events(event):
    """
    Map driver event string to enum.
    """
    if event == "DISTRACTION":
        return DriverEvent.DISTRACTION
    elif event == "FATIGUE":
        return DriverEvent.FATIGUE
    elif event == "DRIVER_REQUEST":
        return DriverEvent.DRIVER_REQUEST
    elif event == "NDRT":
        return DriverEvent.NDRT


class Config:
    """
    Config class that holds the values defined in the different YAML files, including the config file,
    the ttd.yaml file, and the view.yaml file. Entries in this class can easily be update with other settings,
    such as the driver preferences.
    """

    def __init__(self, **entries):
        self.__dict__.update(entries)

        # This is set to False here as a default, but can be updated when route data is used
        self.includes_route_data = False

        # Map the allowed driver events to enums
        driver_events = []
        for event in self.allowed_driver_events:
            driver_events.append(map_driver_events(event))
        self.allowed_driver_events = driver_events

        # Store the allowed static events
        allowed_static_events = {}
        for event in reversed(self.allowed_static_events):
            if event in self.static_events:
                allowed_static_events[event] = self.static_events[event]
            else:
                raise ValueError("{0} is not defined as a static event in the Config file, and therefore cannot be used"
                                 "as an allowed static event.".format(event))
        self.allowed_static_events = allowed_static_events

        # Store the allowed dynamic events
        allowed_dynamic_events = {}
        for event in reversed(self.allowed_dynamic_events):
            if event in self.dynamic_events:
                allowed_dynamic_events[event] = self.dynamic_events[event]
            else:
                raise ValueError("{0} is not defined as a static event in the Config file, and therefore cannot be used"
                                 "as an allowed static event.".format(event))
        self.allowed_dynamic_events = allowed_dynamic_events

        # Evaluate the TTDU values that need to be evaluated
        self.ttdu['distraction']['L0'][0] = eval(self.ttdu['distraction']["L0"][0])
        self.ttdu['distraction']['L2'][0] = eval(self.ttdu['distraction']["L2"][0])
        self.ttdu['ndrt']["L0"][0] = eval(self.ttdu['ndrt']["L0"][0])
        self.ttdu['ndrt']["L3"][0] = eval(self.ttdu['ndrt']["L3"][0])
        self.ttdu['ndrt']["L3"][1] = eval(self.ttdu['ndrt']["L3"][1])
        self.ttdu['ndrt']["L3"][2] = eval(self.ttdu['ndrt']["L3"][2])
        self.ttdu['ndrt']["L3"][3] = eval(self.ttdu['ndrt']["L3"][3])

        # road_length can be used in the config file for the calculation of minimum and maximumg length of road types
        road_length = self.road_length
        # Store the allowed road types and their characteristics
        allowed_road_types = {}
        for road_type in self.allowed_road_types:
            if road_type in self.road_types:
                road_part = self.road_types[road_type]
                min_length = road_part["min_length"]
                if not (isinstance(min_length, float) or isinstance(min_length, int)):
                    road_part["min_length"] = eval(min_length)
                max_length = road_part["max_length"]
                if not (isinstance(max_length, float) or isinstance(max_length, int)):
                    road_part["max_length"] = eval(max_length)
                allowed_road_types[road_type] = road_part
            else:
                raise ValueError("{0} is not defined as a road type in the Config file, and therefore cannot be used "
                                 "as an allowed road type".format(road_type))
        self.allowed_road_types = allowed_road_types
