import os
import sys

# from stable_baselines.common.vec_env import SubprocVecEnv
# from stable_baselines import PPO2
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3 import DQN

from controller.rl_simulator import RLSimulator
from utils import DotDict, except_hook

if __name__ == '__main__':
    # install exception hook: without this, uncaught exception would cause application to exit
    sys.excepthook = except_hook

    settings = DotDict({
        "config_file": os.path.join("rl_config", "distraction_config.yaml"),
        "view_file": "view.yaml",
        "driver_profile": "driver_preferences.yaml",
        "runs": 1,
        "render": False,
        "dir_name": "test_results",
        "road_file": "simple_road.yaml",  # When used, used this file to preset (parts of) the road
        # "log_mediator": "ACTIONS",  # Can be left out (or None), ALL, or ACTIONS
        # "save_fig": "testrun.png",  # When uncommented, saves figures in images directory
        "rl_settings_file": "rl_settings.yaml",
        "rl_method": DQN,  # Used both for training (determines training method) and loading
        "rl_model": "test_model_2",
    })

    # Uncomment the following three lines (and comment settings above) to use run configurations instead
    # from run_configurations.rl.settings import settings
    # from run_configurations.paths import add_path
    # settings = add_path(settings, "rl")

    # Based on the stable baselines package used, import the correct SubprocVecEnv (see commented lines at top of file)
    RLSimulator(settings, SubprocVecEnv).run()
