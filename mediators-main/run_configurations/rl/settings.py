from stable_baselines3 import DQN

from utils import DotDict


settings = DotDict({
    "config_file": "distraction_config.yaml",
    "view_file": "view.yaml",
    "driver_profile": "driver_preferences.yaml",
    "runs": 1,
    "render": True,
    "dir_name": "test_results",
    "road_file": "simple_road.yaml",  # When used, used this file to preset (parts of) the road
    # "log_mediator": "ACTIONS",  # Can be left out (or None), ALL, or ACTIONS
    # "save_fig": "testrun.png",  # When uncommented, saves figures in images directory
    "rl_settings_file": "rl_settings.yaml",
    "rl_method": DQN,  # Used both for training (determines training method) and loading
    "rl_model": "test_model_2",
})
