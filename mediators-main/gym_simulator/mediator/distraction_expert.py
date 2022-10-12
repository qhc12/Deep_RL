from gym_simulator.mediator.mediator import Mediator
from mediator_system.decision_rules.tree_parser import TreeParser


class DistractionExpert(Mediator):
    """
    Mediator system that is focused on distraction use case. This is used for training an expert and creating a dataset
    from this to use for RL.
    """

    def __init__(self, config, tree_file, action_mapper, observation_manager, preferences):
        super().__init__(None, None, None)
        self.config = config
        self.action_mapper = action_mapper
        # These are all possible actions currently defined. Defined here to ensure the decision tree parses correctly
        possible_actions = ['DN', 'CANCEL', 'SSL0', 'SSL2', 'SSL3', 'SSL4', 'ESL0', 'ESL2', 'ESL3', 'ESL4', 'CF', 'CD',
                            'ES', 'PD', 'CR']
        # The available suggestion levels, used to ensure the mediator system does not suggest a higher level
        # than possible
        self.available_sls = sorted([action for action in action_mapper.available_actions if 'SSL' in action])
        # Contains the decision tree
        self.tree = TreeParser(tree_file, possible_actions).parse()
        self.observation_manager = observation_manager
        self.preferences = preferences

    def is_random(self):
        return False

    def get_action(self, env):
        return self.get_expert_action(env.get_observations())

    def get_expert_action(self, observations):
        obs_dict = self.observation_manager.obs_space_class.reverse_transform(observations)
        current_level = obs_dict["current_level"]  # Current level the car is driving in
        ttaf_l2 = obs_dict["ttaf_l2"]
        ttaf_l3 = obs_dict["ttaf_l3"]
        ttaf_l4 = obs_dict["ttaf_l4"]
        max_available_level = self.__get_max_available_level(ttaf_l2, ttaf_l3, ttaf_l4)

        state = {
            'current_level': current_level,
            'max_available_level': max_available_level,
            'distraction': obs_dict["distraction"],
            'ssl4_declined': obs_dict["ssl4_declined"],
            'ttdu': obs_dict["ttdu"],
            'min_esl_time': self.config.min_esl_time,
            'timestep': self.config.timestep
        }
        action, _ = self.tree.evaluate(state)
        return self.action_mapper.get_action_int(action)

    def __get_max_available_level(self, ttaf_l2, ttaf_l3, ttaf_l4):
        """
        Returns the max_available_level, which is the highest available level that is available for at least a short
        period of time. It should be available for at least <switch_time>, to give the mediator system a chance to
        switch the driver to another level. Furthermore, it should be available within the esl time, so that once
        the level is enforced it will be available when enforcement is finished. Finally, since switching takes some
        time, the TTAU in the future position should also be at least bigger than the switch time.

        This variable is mainly used when unsafe situations arise, to briefly shift to a different level.
        """
        max_available_level = "L0"
        if ttaf_l4 == 0:
            max_available_level = "L4"
        elif ttaf_l3 == 0:
            max_available_level = "L3"
        elif ttaf_l2 == 0:
            max_available_level = "L2"
        return min(max_available_level, self.available_sls[-1][2:])

    def set_future_action(self, env):
        raise NotImplementedError("Future actions are not currently available for RL models.")
