from gym_simulator.mediator.future_action import FutureAction
from gym_simulator.mediator.mediator import Mediator
from mediator_system.mediator_interface import MediatorInterface


class TreeMediator(Mediator):
    """
    MEDIATOR for decision trees. Uses logic from a tree file and the current state of the environment to base its
    actions on.
    """

    def __init__(self, config, tree_file, action_mapper, log=None, noise=None, tta_levels="levels"):
        super().__init__(log, noise, tta_levels)
        self.config = config  # This contains both values from config file and preferences file
        self.action_mapper = action_mapper
        self.mediator_interface = MediatorInterface(tree_file, action_mapper.available_actions)
        self.future_action_calculator = FutureAction(self)

    def is_random(self):
        return self.mediator_interface.tree is None

    def get_action(self, env):
        (action, args), updated_state = self.mediator_interface.get_action(self.build_state(env))
        action = self.__update_action(action, env.pending_action, args, env.car.position)
        env.action_args = args
        self.__log(env, updated_state, action, args)
        return self.action_mapper.get_action_int(action)

    def build_state(self, env, ttaf=None, ttau=None, position=None, time_passed=None, is_future_action_state=False):
        """
        Builds a dictionary with variables used in the trees, representing the current state of the environment.
        If defined, noise is added to the state.
        """
        add_noise = self.noise is not None
        ttaf = ttaf if is_future_action_state else env.car.get_ttaf(self.tta_levels)
        ttau = ttau if is_future_action_state else env.car.get_ttau(self.tta_levels)
        ttaf_with_possible_noise = [t + (self.noise["ttaf"] if add_noise and t > 0 else 0) for t in ttaf]
        ttau_with_possible_noise = [t + (self.noise["ttau"] if add_noise and t > 0 else 0) for t in ttau]
        ttdf_with_possible_noise = env.driver.ttdf + (
            self.noise["ttdf"] if add_noise and env.driver.ttdf > 0 else 0)
        ttdu_with_possible_noise = env.driver.ttdu + (
            self.noise["ttdu"] if add_noise and env.driver.ttdu > 0 else 0)

        return {
            "comfortable_shift_time": self.config.comfortable_shift_time,
            "timestep": self.config.timestep,
            "current_level": env.car.current_level,
            "ttaf": ttaf_with_possible_noise,
            "ttau": ttau_with_possible_noise,
            "uncomfortable_switch": self.config.uncomfortable_switch,
            "position": env.car.position if not is_future_action_state else position,
            "speeds": env.road.max_automation_levels.speeds,
            "min_esl_time": self.config.min_esl_time,
            "preferred_level": self.config.preferred_level,
            "time_passed": env.time_passed if not is_future_action_state else time_passed,
            "last_decline": env.driver.last_decline,
            "decline_threshold": self.config.decline_threshold,
            "pending_action": env.pending_action.get_name() if not is_future_action_state and env.pending_action
            else None,
            "time_of_last_switch": env.safety.time_of_last_switch,
            "distraction": env.driver.distraction if not is_future_action_state else 0,
            "fatigue": env.driver.fatigue if not is_future_action_state else 0,
            "uncorrectable_fatigue": env.driver.uncorrectable_fatigue,
            "ttdf": ttdf_with_possible_noise,
            "ttdu": ttdu_with_possible_noise,
            "driver_request": env.driver.driver_request if not is_future_action_state else None,
            "road_length": env.road.total_distance,
            "woo_time": self.config.window_of_opportunity_time
        }

    def __update_action(self, action, pending_action, args, position):
        """
        Update the action returned by the decision tree. If the action returned by the decision tree is the same as the
        action currently pending, nothing should be done, so action is updated to DN. If it's a different action,
        the action currently pending should be canceled, and replaced by this action, so CANCEL<NEW_ACTION> will be the
        action.
        If an ES is about to be made but deemed unnecessary, it is cancelled.
        If an action suggested by the mediator tree is not part of the available actions, do nothing.
        """
        if pending_action and not (action == 'DN' or action == 'CANCEL'):
            name = pending_action.get_name()
            if name == action:
                action = 'DN'
                if 'time' in args and (name.startswith('ESL') or name.startswith('SSL')):
                    pending_action.remaining_time = args['time']
                if 'last' in args:
                    pending_action.update_latest_start(position, args['last'])
            else:
                action = 'CANCEL' + action
        elif pending_action and pending_action.get_name() == 'ES' and action == 'DN':
            action = 'CANCEL' + action

        if action not in self.action_mapper.available_actions:
            action = 'DN'
        return action

    def __log(self, env, state, action, args):
        if self.log == "ALL" or (self.log == "ACTIONS" and not action == "DN"):
            print(env.car.position)
            print(state)
            print(self.mediator_interface.tree.get_evaluation_path(state))
            print(action + " " + str(args) + "\n")

    def set_future_action(self, env):
        env.future_action = self.future_action_calculator.get_future_action(env)
