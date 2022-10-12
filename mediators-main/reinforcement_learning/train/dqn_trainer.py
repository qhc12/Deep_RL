from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.evaluation import evaluate_policy

from gym_simulator.envs import MediatorEnv
from reinforcement_learning.train.abstract_trainer import AbstractTrainer


class DQNTrainer(AbstractTrainer):
    """
    DQN Trainer in Stabe Baselines3.
    """

    def __init__(self, settings):
        super().__init__(settings, DQN)
        vec_env = make_vec_env(MediatorEnv, env_kwargs=self.env_args, n_envs=settings.n_processes)
        self.eval_env = MediatorEnv(**self.env_args)
        check_env(self.eval_env)
        model_args = {
            "policy": "MlpPolicy",
            "env": vec_env,
            "verbose": 1
        }

        self.model = DQN(**model_args)

    def learn(self):
        mean_reward, std_reward = evaluate_policy(self.model, self.eval_env, n_eval_episodes=10)
        print(f'Mean reward: {mean_reward} +/- {std_reward:.2f}')
        self.model.learn(total_timesteps=self.timesteps)
        mean_reward, std_reward = evaluate_policy(self.model, self.eval_env, n_eval_episodes=10)
        print(f'Mean reward: {mean_reward} +/- {std_reward:.2f}')

    def get_rl_settings(self):
        return self.eval_env.rl_settings

    def get_model(self):
        return self.model
