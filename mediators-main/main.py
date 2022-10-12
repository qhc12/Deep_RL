import os
import sys

from controller.tree_simulator import TreeSimulator
from utils import DotDict, except_hook

if __name__ == '__main__':
    # install exception hook: without this, uncaught exception would cause application to exit
    sys.excepthook = except_hook

    settings = DotDict({
        "config_file": "config.yaml",
        "view_file": "view.yaml",
        "driver_profile": "driver_preferences.yaml",
        "tree_files": ["mediator.tree"],
        # "noise": {  # Specifies noise for the 4 parameters. Each list should have the same length.
        #     "ttaf": [0, -20],
        #     "ttau": [0, 20],
        #     "ttdf": [0, 0],
        #     "ttdu": [0, 0]
        # },
        # Levels to use: can be "levels", "optimistic_levels", or "pessimistic_levels"
        # "tta_levels": "pessimistic_levels",
        "runs": 1,
        "render": True,
        "dir_name": "test",
        "no_threads": 1,
        # When used, used this file to preset (parts of) the road
        # "road_file": os.path.join("sweden_route", "new_route.yaml"),
        # "include_road_data": True,
        # "route_data_file": os.path.join("sweden_route", "route_data.pkl"),
        # "log_mediator": "ACTIONS",  # Can be left out (or None), ALL, or ACTIONS
        # "save_fig": "testrun.png",  # When uncommented, saves figures in images directory
    })

    if settings.render and settings.no_threads > 1:
        sys.stderr.write('WARNING: When rendering is enabled, multithreaded running is unavailable.\n')

    TreeSimulator(settings).run()
