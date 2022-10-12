import sys

from gym_simulator.config.allowed_values import RoadEventType
from gym_simulator.evaluation.safety_types import SafetyType


class Data:
    """
    Class to hold all (historical) data of the simulation. Currently used for visualisation and result purposes.
    """

    def __init__(self, env):
        # Most of the data only needs to be initialized and stored when rendering. Only safety events need to be
        # logged in all cases because these are documented in the results
        if env.allow_render:
            self.config = env.config
            self.max_automation_levels = env.road.max_automation_levels.levels  # The max automation levels array
            self.optimistic_automation_levels = env.road.max_automation_levels.optimistic_levels
            self.pessimistic_automation_levels = env.road.max_automation_levels.pessimistic_levels
            self.current_levels = [env.car.current_level]  # Array with current level for each step
            self.positions = [env.car.position]
            self.speeds = [env.car.speed]
            self.times = [env.time_passed]
            self.road_parts = env.road.road_parts  # The road parts
            self.road_length = env.road.total_distance
            self.estimated_total_time = env.road.estimated_total_time
            self._update_events(env)

            self.ttaf = self._init_ttaf(env)
            self.optimistic_ttaf = self._init_ttaf(env, "optimistic_levels")
            self.pessimistic_ttaf = self._init_ttaf(env, "pessimistic_levels")
            self.real_ttaf = {
                "L2": [],
                "L3": [],
                "L4": []
            }
            self.real_route_ttaf_l2 = [env.car.get_parsed_ttaf_l2()]

            self.ttau = self._init_ttau(env)
            self.optimistic_ttau = self._init_ttau(env, "optimistic_levels")
            self.pessimistic_ttau = self._init_ttau(env, "pessimistic_levels")
            self.real_ttau = {
                "L2": [],
                "L3": [],
                "L4": []
            }
            self.real_route_ttau_l2 = [env.car.get_parsed_ttau_l2()]

            self._update_driver_events(env)
            self.fatigue = [env.driver.fatigue]  # Fatigue history
            self.distraction = [env.driver.distraction if env.driver.ndrt == 0 else None]  # Distraction history
            self.driver_request = [env.driver.driver_request]
            self.ndrt = [env.driver.ndrt if env.driver.ndrt > 0 else None]  # NDRT history
            self.ttdf = [self.estimated_total_time if env.driver.ttdf == sys.maxsize else env.driver.ttdf]  # TTDF history
            self.ttdu = [self.estimated_total_time if env.driver.ttdu == sys.maxsize else env.driver.ttdu]  # TTDU history
            self.actions = {}  # Action history
            self.future_actions = {}  # Future actions
            self.evaluation = {}
            self.last_step_was_active = {}
            for safety_type in SafetyType:
                self.evaluation[safety_type] = {'start': [], 'end': []}
                self.last_step_was_active[safety_type] = False

        self._update_safety_events(env)

    def update(self, env):
        """
        Update necessary data for current timestep.
        """
        if env.allow_render:
            self.max_automation_levels = env.road.max_automation_levels.levels
            self.optimistic_automation_levels = env.road.max_automation_levels.optimistic_levels
            self.pessimistic_automation_levels = env.road.max_automation_levels.pessimistic_levels
            self.current_levels.append(env.car.current_level)
            self.positions.append(env.car.position)
            self.speeds.append(env.car.speed)
            self.times.append(env.time_passed)
            self._update_events(env)

            self._update_ttaf(env, self.ttaf)
            self._update_ttaf(env, self.optimistic_ttaf, "optimistic_levels")
            self._update_ttaf(env, self.pessimistic_ttaf, "pessimistic_levels")
            self.real_route_ttaf_l2.append(env.car.get_parsed_ttaf_l2())

            self._update_ttau(env, self.ttau)
            self._update_ttau(env, self.optimistic_ttau, "optimistic_levels")
            self._update_ttau(env, self.pessimistic_ttau, "pessimistic_levels")
            self.real_route_ttau_l2.append(env.car.get_parsed_ttau_l2())

            self._update_real_tta(env)

            self._update_driver_events(env)
            self.fatigue.append(env.driver.fatigue)
            self.distraction.append(env.driver.distraction if env.driver.ndrt == 0 else None)
            self.driver_request.append(env.driver.driver_request)
            self.ndrt.append(env.driver.ndrt if env.driver.ndrt > 0 or (self.ndrt[-1] is not None and self.ndrt[-1] > 0)
                             else None)
            if self.ndrt[-1] is not None and self.ndrt[-1] > 0 and \
                    self.distraction[-2] is not None and self.distraction[-2] == 0:
                self.ndrt[-2] = 0
            self.ttdf.append(env.driver.ttdf)
            self.ttdu.append(env.driver.ttdu)
            if env.last_action:
                action = env.last_action
                key = action.get_name()
                if key in self.actions:
                    self.actions[key].append(action)
                else:
                    self.actions[key] = [action]

            if env.future_action:
                future_action = env.future_action
                key = future_action.get_name()
                if key in self.future_actions:
                    self.future_actions[key].append(future_action)
                else:
                    self.future_actions[key] = [future_action]
            self._update_evaluation(env)

        self._update_safety_events(env)

    def _init_ttaf(self, env, level_type="levels"):
        ttaf = env.car.get_ttaf(level_type)
        return {  # Dictionary with history of TTAF for all automation levels
            "L2": [ttaf[0]],
            "L3": [ttaf[1]],
            "L4": [ttaf[2]]
        }

    def _update_ttaf(self, env, ttaf_history, level_type="levels"):
        ttaf = env.car.get_ttaf(level_type)
        ttaf_history["L2"].append(ttaf[0])
        ttaf_history["L3"].append(ttaf[1])
        ttaf_history["L4"].append(ttaf[2])

    def _init_ttau(self, env, level_type="levels"):
        ttau = env.car.get_ttau(level_type)
        return {  # Dictionary with history of TTAU for all automation levels
            "L2": [ttau[0]],
            "L3": [ttau[1]],
            "L4": [ttau[2]]
        }

    def _update_ttau(self, env, ttau_history, level_type="levels"):
        ttau = env.car.get_ttau(level_type)
        ttau_history["L2"].append(ttau[0])
        ttau_history["L3"].append(ttau[1])
        ttau_history["L4"].append(ttau[2])

    def _update_real_tta(self, env):
        # Calculates the real TTAF and TTAU values after a relevant maximum level change occurs, by calculating
        # how long the previous piece of road took to drive
        if len(self.positions) < 2:
            return

        max_levels = env.road.max_automation_levels.levels
        prev_position = self.positions[-2]
        cur_position = self.positions[-1]
        # Indicates a max available level change, so real TTAF for previous part can be calculated
        if any(prev_position < entry[1] < cur_position for entry in max_levels) or env.done:
            indices = [i for i, entry in enumerate(max_levels) if prev_position < entry[1] < cur_position]
            if len(indices) == 0 and env.done:
                indices = [next(i + 1 if i < len(max_levels) - 1 else i for i, entry in enumerate(max_levels) if entry[1] < cur_position and
                                (i == len(max_levels) - 1 or cur_position < max_levels[i + 1][1]))]
            for index in indices:
                cur_max_level = max_levels[index][0]
                next_max_level = None if index >= len(max_levels) - 1 or env.done else max_levels[index + 1][0]
                for level in ["L2", "L3", "L4"]:
                    if next_max_level is None or env.done or cur_max_level >= level > next_max_level \
                            or cur_max_level < level <= next_max_level:
                        if cur_max_level >= level:
                            start = next((max_level[1] for max_level in reversed(max_levels[:index])
                                          if max_level[0] < level), 0.0)
                        else:
                            start = next((max_level[1] for max_level in reversed(max_levels[:index])
                                          if max_level[0] >= level), 0.0)
                        end = max_levels[index][1] if not env.done else cur_position
                        start_position_index = next(i for i, pos in enumerate(self.positions) if pos >= start)
                        end_position_index = next(i for i, pos in enumerate(self.positions) if pos >= end)

                        time_passed_end = self.times[end_position_index]
                        if end >= self.road_length or env.done:
                            end_position_index += 1

                        for i, position in enumerate(self.positions[start_position_index:end_position_index]):
                            start_time_passed_index = start_position_index + i
                            if cur_max_level < level:
                                self.real_ttau[level].append(0)
                            elif index == len(max_levels) - 1 and cur_max_level >= level:
                                self.real_ttau[level].append(sys.maxsize)
                            else:
                                self.real_ttau[level].append(
                                    round(time_passed_end - self.times[start_time_passed_index], 2))

                            if cur_max_level >= level:
                                self.real_ttaf[level].append(0)
                            elif index == len(max_levels) - 1 and cur_max_level < level:
                                self.real_ttaf[level].append(sys.maxsize)
                            else:
                                self.real_ttaf[level].append(
                                    round(time_passed_end - self.times[start_time_passed_index], 2))

    def _update_events(self, env):
        self.road_events = {  # Dictionary with static and dynamic road events
            "static": {},
            "dynamic": {}
        }

        for allowed_static_event in self.config.allowed_static_events:
            self.road_events["static"][allowed_static_event] = []
        for allowed_dynamic_event in self.config.allowed_dynamic_events:
            self.road_events["dynamic"][allowed_dynamic_event] = []

        for event in env.road.event_manager.events:
            if event.event_type == RoadEventType.STATIC:
                self.road_events["static"][event.name].append(event)
            elif event.event_type == RoadEventType.DYNAMIC:
                self.road_events["dynamic"][event.name].append(event)

    def _update_driver_events(self, env):
        self.driver_events = {}
        for allowed_driver_event in self.config.allowed_driver_events:
            self.driver_events[allowed_driver_event] = []
        for event in env.driver.all_events:
            self.driver_events[event.get_enum()].append(event)

    def _update_evaluation(self, env):
        safety_events = env.safety
        for safety_type in SafetyType:
            current_step_is_active = safety_events.current_step_is_active[safety_type]
            if current_step_is_active:
                if self.last_step_was_active[safety_type]:
                    self.evaluation[safety_type]['end'][-1] = self.positions[-1]
                else:
                    self.evaluation[safety_type]['start'].append(self.positions[-1])
                    self.evaluation[safety_type]['end'].append(self.positions[-1])
            elif self.last_step_was_active[safety_type]:
                self.evaluation[safety_type]['end'][-1] = self.positions[-1]
            self.last_step_was_active[safety_type] = current_step_is_active

    def _update_safety_events(self, env):
        self.safety_events = {}
        for possible_event in env.safety.possible_events:
            self.safety_events[possible_event.get_name()] = []
        for event in env.safety.all_events:
            self.safety_events[event.name].append(event)
