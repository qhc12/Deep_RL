import os

from stable_baselines.gail import generate_expert_traj

from globals import ROOT_DIR
from gym_simulator.envs import MediatorEnv
from gym_simulator.mediator.distraction_expert import DistractionExpert


def create_expert(settings, env):
    """
    Returns expert mediator based on tree.
    """
    if settings.expert == "distraction_expert":
        return DistractionExpert(env.config, settings.tree, env.action_mapper, env.observation_manager,
                                 env.driver_preferences)
    else:
        raise Exception("{0} is not a valid expert".format(settings.expert))


def create_expert_dataset(settings):
    """
    Returns expert dataset based on decision tree.
    """
    save_dir = os.path.join(ROOT_DIR, "expert_datasets")
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    env = MediatorEnv(settings.config_file, settings.driver_profile, settings.view_file,
                      road_file=settings.get("road_file", None), include_road_data=False,
                      rl_settings_file=settings.rl_settings_file)
    mediator = create_expert(settings, env)
    generate_expert_traj(mediator.get_expert_action, os.path.join(save_dir, settings.save_as), env,
                         n_episodes=settings.n_episodes)
