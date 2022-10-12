from mediator_system.decision_rules.tree_parser import TreeParser
from mediator_system.util import DotDict, level_index, get_position_in_time


class MediatorInterface:
    """
    MediatorInterface class, which represents the actual MediatorInterface system and is used to determine the
    appropriate actions given a state.
    """

    def __init__(self, tree_file, available_actions):
        # These are all possible actions currently defined. Defined here to ensure the decision tree parses correctly
        possible_actions = ['DN', 'CANCEL', 'SSL0', 'SSL2', 'SSL3', 'SSL4', 'ESL0', 'ESL2', 'ESL3', 'ESL4', 'CF', 'CD',
                            'ES', 'PD', 'CR']
        # The available suggestion levels, used to ensure the mediator system does not suggest a higher level
        # than possible
        self.available_sls = sorted([action for action in available_actions if 'SSL' in action])
        # Contains the decision tree
        self.tree = TreeParser(tree_file, possible_actions).parse()

    def get_action(self, parameters):
        """
        Get action.
        """
        variables = DotDict(parameters)
        current_level = variables.current_level  # Current level the car is driving in
        ttau_current = None if current_level == 'L0' else variables.ttau[level_index(current_level)]

        # This is the minimum time needed to comfortable enforce a driver to another level
        comfortable_enforce_time = variables.woo_time + variables.comfortable_shift_time + variables.timestep
        # This is the minimum time available needed in a level to make it comfortable for the driver to switch to that
        # level
        minimum_availability_time = variables.comfortable_shift_time + variables.uncomfortable_switch \
            + comfortable_enforce_time
        # Minimum time needed to enforce a driver to another level
        minimum_enforce_time = variables.min_esl_time + variables.ttdf + variables.timestep
        # Minimum time needed to initiate ESL action at end of WOO
        latest_enforce_time = variables.comfortable_shift_time + variables.timestep

        max_level_long = self.__get_max_level_long(minimum_availability_time, *variables.ttaf, *variables.ttau)
        # Get the last position at which max level long is still available for L2. Can easily be extended for L3/L4.
        latest_max_level_long_position = self.__get_latest_max_level_long_position(variables.speeds, variables.position,
                                                                                   minimum_availability_time,
                                                                                   variables.ttau[0])
        max_available_level = self.__get_max_available_level(comfortable_enforce_time, minimum_enforce_time,
                                                             *variables.ttaf, *variables.ttau)
        # Get the last position at which esl can still be initiated comfortably
        latest_esl_position = self.__get_latest_esl_position(variables.speeds, variables.position, latest_enforce_time,
                                                             variables.ttau[0])

        preferred_level = variables.preferred_level
        ssl0_declined, ssl2_declined, ssl3_declined, ssl4_declined, preferred_level_declined = \
            self.__get_declined_levels(variables, preferred_level, variables.time_passed)

        moving_to = self.__get_moving_to(variables.pending_action)
        comfortable_switch = self.__get_comfortable_switch(variables)

        state = {
            'current_level': current_level,
            'preferred_level': preferred_level,
            'moving_to_level': moving_to,
            'max_level_long': max_level_long,
            'latest_max_level_long_position': latest_max_level_long_position,
            'max_available_level': max_available_level,
            'latest_esl_position': latest_esl_position,
            'distraction': variables.distraction,
            'fatigue': variables.fatigue,
            'uncorrectable_fatigue': variables.uncorrectable_fatigue,
            'ssl4_declined': ssl4_declined,
            'ssl3_declined': ssl3_declined,
            'ssl2_declined': ssl2_declined,
            'ssl0_declined': ssl0_declined,
            'preferred_level_declined': preferred_level_declined,
            'comfortable_switch': comfortable_switch,
            'ttau': ttau_current,
            'ttau_l4': variables.ttau[2],
            'ttau_l3': variables.ttau[1],
            'ttau_l2': variables.ttau[0],
            'ttdf': variables.ttdf,
            'ttdu': variables.ttdu,
            'min_esl_time': variables.min_esl_time,
            'timestep': variables.timestep,
            'active_request': variables.driver_request is not None,
            'driver_request': variables.driver_request,
            'road_length': variables.road_length
        }

        return self.tree.evaluate(state), state

    def __get_max_level_long(self, minimum_availability_time, ttaf_l2, ttaf_l3, ttaf_l4, ttau_l2, ttau_l3, ttau_l4):
        """
        Returns the max_level_long, which is the highest available level that is available for a longer period of time.
        (minimum_availability_time). Furthermore, the max_level_long can never be higher than the highest available
        shift suggestion action.
        """
        max_level_long = "L0"
        if ttaf_l4 == 0 and ttau_l4 > minimum_availability_time:
            max_level_long = "L4"
        elif ttaf_l3 == 0 and ttau_l3 > minimum_availability_time:
            max_level_long = "L3"
        elif ttaf_l2 == 0 and ttau_l2 > minimum_availability_time:
            max_level_long = "L2"
        return min(max_level_long, self.available_sls[-1][2:])

    def __get_latest_max_level_long_position(self, speeds, position, minimum_availability_time, ttau):
        """
        Get the latest position at which max level long for level specified by ttau is still available.
        """
        if ttau <= minimum_availability_time:
            return None
        return get_position_in_time(speeds, position, ttau - minimum_availability_time)

    def __get_max_available_level(self, comfortable_enforce_time, minimum_enforce_time, ttaf_l2, ttaf_l3, ttaf_l4,
                                  ttau_l2, ttau_l3, ttau_l4):
        """
        Returns the max_available_level, which is the highest available level that is available for at least a short
        period of time. It should be available for at least comfortable_enforce_time + minimum_enforce_time, to give
        the driver the chance to comfortably shift to another level, after which there still needs to be enough time
        to be able enforce a shift away from that level again, hence the minimum_enforce_time.
        ttaf should be 0, such that the level is available right now.
        """
        max_available_level = "L0"
        if ttau_l4 > comfortable_enforce_time + minimum_enforce_time and ttaf_l4 == 0:
            max_available_level = "L4"
        elif ttau_l3 > comfortable_enforce_time + minimum_enforce_time and ttaf_l3 == 0:
            max_available_level = "L3"
        elif ttau_l2 > comfortable_enforce_time + minimum_enforce_time and ttaf_l2 == 0:
            max_available_level = "L2"
        return min(max_available_level, self.available_sls[-1][2:])

    def __get_latest_esl_position(self, speeds, position, latest_enforce_time, ttau):
        """
        Get latest position at which ESL can still be comfortably executed, used for WOO.
        """
        if ttau <= latest_enforce_time:
            return None
        return get_position_in_time(speeds, position, ttau - latest_enforce_time)

    def __get_declined_levels(self, variables, preferred_level, cur_time):
        """
        Returns for each level a boolean indicating whether the level has been declined recently, where recently is
        defined as the declines threshold specified in the driver preferences. If a level has recently been declined,
        it is not desirable to suggest it again.
        """
        last_decline = variables.last_decline
        decline_threshold = variables.decline_threshold
        ssl4_declined = last_decline['L4'] is not None and cur_time - last_decline['L4'] < decline_threshold
        ssl3_declined = last_decline['L3'] is not None and cur_time - last_decline['L3'] < decline_threshold
        ssl2_declined = last_decline['L2'] is not None and cur_time - last_decline['L2'] < decline_threshold
        ssl0_declined = last_decline['L0'] is not None and cur_time - last_decline['L0'] < decline_threshold
        preferred_level_declined = last_decline[preferred_level] is not None and \
            cur_time - last_decline[preferred_level] < decline_threshold
        return ssl0_declined, ssl2_declined, ssl3_declined, ssl4_declined, preferred_level_declined

    def __get_moving_to(self, pending_action):
        """
        If the mediator system is currently in the process of (possibly) moving to another level, this level is returned
        here.
        """
        if pending_action is not None and (pending_action.startswith("SSL") or
                                           pending_action.startswith("ESL")):
            return pending_action[2:]
        return None

    def __get_comfortable_switch(self, variables):
        """
        Returns comfortable_switch, which indicates if a comfortable switch can be made, i.e. the last switch was a long
        time ago, where long is defined as the uncomfortable_switch preference.
        """
        last_switch = variables.time_of_last_switch
        return last_switch is None or variables.time_passed - last_switch > variables.uncomfortable_switch
