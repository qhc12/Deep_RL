import os
import sys

from reinforcement_learning.train.dqn_trainer import DQNTrainer
# from reinforcement_learning.train.ppo2_sb_old_trainer import PPO2Trainer

from utils import except_hook, DotDict

if __name__ == '__main__':
    sys.excepthook = except_hook

    # Can be with or without dataset
    settings = DotDict({
        "config_file": os.path.join("rl_config", "distraction_config.yaml"),
        "view_file": "view.yaml",
        "driver_profile": "driver_preferences.yaml",
        "road_file": "simple_road.yaml",
        "rl_settings_file": "rl_settings.yaml",
        "save_as": "test_model_2",
        "n_processes": 12,
        "timesteps": 100
    })

    # dataset = "distraction_expert_dataset_v2.npz"
    # PPO2Trainer(settings, dataset).train()

    DQNTrainer(settings).train()
