import os

from stable_baselines.common.env_checker import check_env
from stable_baselines.common.evaluation import evaluate_policy
from stable_baselines.gail import ExpertDataset
from stable_baselines import PPO2

from globals import ROOT_DIR
from gym_simulator.envs import MediatorEnv
from reinforcement_learning.train.abstract_trainer import AbstractTrainer


class PPO2Trainer(AbstractTrainer):
    """
    A PPO Trainer in Stable Baselines 2, which uses an Expert Dataset as the basis of its training.
    """

    def __init__(self, settings, dataset):
        super().__init__(settings, PPO2)
        env = MediatorEnv(**self.env_args)
        self.eval_env = MediatorEnv(**self.env_args)
        check_env(self.eval_env)
        model_args = {
            "policy": "MlpPolicy",
            "env": env,
            "verbose": 1,
        }
        self.dataset = ExpertDataset(expert_path=os.path.join(ROOT_DIR, "expert_datasets", dataset),
                                     traj_limitation=10, verbose=1)
        self.model = PPO2(**model_args)

    def learn(self):
        self.__pretrain()
        self.__learn()

    def get_rl_settings(self):
        return self.eval_env.rl_settings

    def __learn(self):
        mean_reward, std_reward = evaluate_policy(self.model, self.eval_env, n_eval_episodes=10)
        print(f'Mean reward: {mean_reward} +/- {std_reward:.2f}')
        self.model.learn(total_timesteps=self.timesteps)
        mean_reward, std_reward = evaluate_policy(self.model, self.eval_env, n_eval_episodes=10)
        print(f'Mean reward: {mean_reward} +/- {std_reward:.2f}')

    def __pretrain(self):
        mean_reward, std_reward = evaluate_policy(self.model, self.eval_env, n_eval_episodes=10)
        print(f'Mean reward: {mean_reward} +/- {std_reward:.2f}')
        self.model.pretrain(self.dataset, n_epochs=self.timesteps)
        mean_reward, std_reward = evaluate_policy(self.model, self.eval_env, n_eval_episodes=10)
        print(f'Mean reward: {mean_reward} +/- {std_reward:.2f}')

    def get_model(self):
        return self.model
