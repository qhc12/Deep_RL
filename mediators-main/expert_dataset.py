import os
import sys

from reinforcement_learning.expert import create_expert_dataset

from utils import except_hook, DotDict

if __name__ == '__main__':
    sys.excepthook = except_hook

    settings = DotDict({
        "view_file": "view.yaml",
        "config_file": os.path.join("rl_config", "distraction_config.yaml"),
        "driver_profile": "driver_preferences.yaml",
        # "road_file": "simple_road.yaml",
        "rl_settings_file": "rl_settings.yaml",
        "tree": "distraction_wo_es.tree",
        "expert": "distraction_expert",
        "n_episodes": 100,
        "save_as": "distraction_expert_dataset_v3",
    })

    create_expert_dataset(settings)
