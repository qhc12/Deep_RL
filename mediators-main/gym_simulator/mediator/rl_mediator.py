from gym_simulator.mediator.mediator import Mediator


class RLMediator(Mediator):
    """
    MEDIATOR for RL. Uses a trained model and observations from the environment to base its actions on.
    """

    def __init__(self, model, log=None, noise=None, tta_levels="levels"):
        super().__init__(log, noise, tta_levels)
        self.model = model

    def is_random(self):
        return False

    def get_action(self, env):
        obs = env.get_observations()
        action, _ = self.model.predict(obs)
        self.__log(env, env.obs_arr_to_dict(obs), env.action_mapper.get_action_string(action))
        return action

    def __log(self, env, state, action):
        if self.log == "ALL" or (self.log == "ACTIONS" and not action == "DN"):
            print(env.car.position)
            print(state)
            print(action + "\n")

    def set_future_action(self, env):
        raise NotImplementedError("Future actions are not currently available for RL models.")
