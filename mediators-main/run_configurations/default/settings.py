from utils import DotDict


settings = DotDict({
    "config_file": "l2_config.yaml",
    "view_file": "view.yaml",
    "driver_profile": "driver_preferences.yaml",
    "tree_files": ["L2_mediator.tree"],
    # "noise": {  # Specifies noise for the 4 parameters. Each list should have the same length.
    #     "ttaf": [0, -20],
    #     "ttau": [0, 20],
    #     "ttdf": [0, 0],
    #     "ttdu": [0, 0]
    # },
    # "tta_levels": "pessimistic_levels",  # Levels to use: can be "levels", "optimistic_levels", or "pessimistic_levels"
    "runs": 1,
    "render": True,
    "dir_name": "default",
    "no_threads": 10,
    "road_file": "new_route.yaml",  # When used, used this file to preset (parts of) the road
    "include_road_data": True,
    "route_data_file": "route_data.pkl",
    # "log_mediator": "ACTIONS",  # Can be left out (or None), ALL, or ACTIONS
    # "save_fig": "testrun.png",  # When uncommented, saves figures in images directory
})
