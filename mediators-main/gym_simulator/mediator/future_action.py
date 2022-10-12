import sys


class FutureAction:
    """
    Class to calculate actions that are coming up in the future, related to shifting levels up and down (since driver
    states cannot be predicted).
    """

    def __init__(self, mediator):
        self.config = mediator.config
        self.action_mapper = mediator.action_mapper
        self.mediator_interface = mediator.mediator_interface
        self.mediator = mediator

    def get_future_action(self, env):
        """
        Predicts the next action (related to shift changes) that MEDIATOR will suggest and returns it.
        """
        future_position = self.__get_future_position(env)
        action = 'DN'
        args = None
        final_state = {}
        if future_position < env.road.total_distance:
            action, args, final_state = self.__query_tree(env, future_position)
        future_action = None if action == "DN" else \
            self.action_mapper.map_actions(self.action_mapper.get_action_int(action), args, env)
        if future_action:
            future_action.start = future_position
            future_action.end = future_position + env.road.get_road_part(future_action.start)\
                .get_travel_distance(future_action.remaining_time)

        if future_action and future_action.get_name() in env.data.future_actions:
            last_future_action = env.data.future_actions[future_action.get_name()][-1]
            if abs(last_future_action.start - future_action.start) < 0.1 or \
                    abs(last_future_action.end - future_action.start) < 0.1:
                future_action = None

        return future_action

    def __query_tree(self, env, position):
        """
        Queries the decision tree from the given position.
        """
        ttaf = env.road.max_automation_levels.get_ttaf(position)
        ttau = env.road.max_automation_levels.get_ttau(position)
        time_passed = env.time_passed + env.road.current_road_part.get_travel_time(position - env.car.position)
        (action, args), final_state = self.mediator_interface.get_action(
            self.mediator.build_state(env, ttaf, ttau, position, time_passed, True))
        if action not in self.action_mapper.available_actions or \
                not (action.startswith('SSL') or action.startswith('ESL')):
            action = "DN"
        return action, args, final_state

    def __get_future_position(self, env):
        """
        Gets the future position at which to calculate a new action.
        """
        current_position = env.car.position
        next_level_change, is_level_incresae = self.__get_next_level_change(env)
        if is_level_incresae:
            return max(next_level_change, self.__get_decline_position(env), self.__get_comfortable_switch_position(env))
        else:
            return max(current_position, next_level_change)

    def __get_decline_position(self, env):
        """
        Returns minimum distance that needs to be travelled before any shift level can be suggested again after a
        decline.
        """
        available_levels = [level for level in ["L2", "L3", "L4"] if level <= self.config.maximum_automation_level]
        decline_position = sys.maxsize
        for level in available_levels:
            last_decline = env.driver.last_decline[level]
            if last_decline:
                decline_threshold_time_remaining = max(0, self.config.decline_threshold -
                                                       (env.time_passed - last_decline))
                decline_position = min(decline_position, env.road.get_position_in_time(
                    env.car.position, decline_threshold_time_remaining))
            else:
                return env.car.position
        return decline_position

    def __get_comfortable_switch_position(self, env):
        """
        Returns minimum distance that needs to be traveled before a shift to another level can be made comfortably.
        """
        last_switch = env.safety.time_of_last_switch
        if last_switch:
            switch_time_remaining = max(0, self.config.uncomfortable_switch - (env.time_passed - last_switch))
            return env.road.get_position_in_time(env.car.position, switch_time_remaining)
        return env.car.position

    def __get_next_level_change(self, env):
        """
        Returns the position at which the next level change occurs. If this is a change down to a lower level,
        the position just before the change is taken, because the system needs to give the driver time to shift down.
        """
        max_auto_levels = env.road.max_automation_levels
        levels = max_auto_levels.levels
        current_levels_index = max_auto_levels.get_index_of_current_level(env.car.position)
        next_level_change = levels[current_levels_index][1]
        current_available_level = levels[current_levels_index][0]
        next_available_level = levels[current_levels_index + 1][0] if current_levels_index < len(levels) - 1 else \
            current_available_level

        speed = next(speed for i, (speed, end) in enumerate(max_auto_levels.speeds) if end >= next_level_change and
                     (i == 0 or next_level_change > max_auto_levels.speeds[i - 1][1]))
        if current_available_level > next_available_level:
            next_level_change -= (((self.config.comfortable_shift_time + 2 * self.config.timestep) * speed) / 3600)
        return next_level_change, next_available_level > current_available_level
