import sys

from gym_simulator.evaluation.safety_types import SafetyType


class EvaluationMetrics:
    """
    Class to keep track of evaluation metrics of a single run.
    """

    def __init__(self, config, safety):
        self.config = config
        self.safety = safety

        self.safety_type_event_count = {}
        self.safety_type_total_event_time = {}
        self.safety_type_avg_event_time = {}
        self.safety_type_time_ratio = {}
        self.safety_type_current_event_duration = {}
        self.safety_type_shortest_event = {}
        self.safety_type_longest_event = {}
        self.safety_type_prev_step_active = {}
        self.safety_type_events_per_name = {}
        for st in SafetyType:
            self.safety_type_event_count[st] = 0
            self.safety_type_total_event_time[st] = 0
            self.safety_type_avg_event_time[st] = 0.0
            self.safety_type_time_ratio[st] = 0.0
            self.safety_type_current_event_duration[st] = 0.0
            self.safety_type_shortest_event[st] = float(sys.maxsize)
            self.safety_type_longest_event[st] = 0.0
            self.safety_type_prev_step_active[st] = False
        self.safety_type_events_per_name = {}

        self.action_frequency = 0  # The number of actions per 100 KM
        self.action_count = 0  # The number of actions in a simulation
        # Average time between the end of the previous action and the start of the next
        self.avg_time_between_actions = 0.0
        self.total_time_between_actions = 0.0  # Total time between starts and ends of actions
        self.time_of_last_action = None  # Timestamp of the end of the last action
        self.start_first_action = None  # Start time of first action
        self.total_time_without_actions = 0.0  # Total time where no action is performed

        self.time_driven_in_level = {
            "L0": 0.0,
            "L2": 0.0,
            "L3": 0.0,
            "L4": 0.0
        }

        self.made_es = False  # Set to True if the car made an Emergency Stop

    def step(self, action_started, action_pending, action_ended, current_level, cur_time):
        """
        Takes an evaluation step with 3 booleans and the current time in the simulation (is time in seconds since the
        start).
        action_started is True if a new action started this timestep.
        action_pending is True if there is an action pending in the current timestep.
        action_ended is True if an action was resolved in the current timestep.
        Based on these variables and the current time, various variables in the evaluation are updated.
        """
        self.time_driven_in_level[current_level] = self.time_driven_in_level[current_level] + self.config.timestep

        for st in SafetyType:
            cur_step_active = self.safety.current_step_is_active[st]
            if cur_step_active:
                self.safety_type_total_event_time[st] += self.config.timestep
                if not self.safety_type_prev_step_active[st]:
                    self.safety_type_event_count[st] += 1
                    self.safety_type_current_event_duration[st] = self.config.timestep
                else:
                    self.safety_type_current_event_duration[st] += self.config.timestep

                if self.safety_type_current_event_duration[st] > self.safety_type_longest_event[st]:
                    self.safety_type_longest_event[st] = self.safety_type_current_event_duration[st]
                if self.safety_type_current_event_duration[st] < self.safety_type_shortest_event[st]:
                    self.safety_type_shortest_event[st] = self.safety_type_current_event_duration[st]

            self.safety_type_prev_step_active[st] = cur_step_active

        if action_started:
            self.action_count = self.action_count + 1
            if self.time_of_last_action is not None:
                # Increase the total time between actions with the time between the start of the action started in this
                # timestep and the timestep at which the last action ended
                self.total_time_between_actions = self.total_time_between_actions \
                                                  + (cur_time - self.time_of_last_action)
            else:
                self.start_first_action = cur_time

        if action_pending or action_ended:
            # If an action ended or is pending, update the timestamp of the last action
            self.time_of_last_action = cur_time

    def finalize(self, data, time_passed):
        """
        Calculates several averages when the simulation has finished.
        """
        for st in SafetyType:
            try:
                self.safety_type_avg_event_time[st] = self.safety_type_total_event_time[st] / \
                                                      float(self.safety_type_event_count[st])
            except ZeroDivisionError:
                self.safety_type_avg_event_time[st] = 0.0
            self.safety_type_time_ratio[st] = self.safety_type_total_event_time[st] / time_passed

        for possible_event in self.safety.possible_events:
            event_type = possible_event.get_name()
            safety_events = data.safety_events[event_type]
            count = len(safety_events)
            duration = sum([safety_event.duration for safety_event in safety_events])
            self.safety_type_events_per_name[possible_event.get_name()] = {'Count': count, 'Total duration': duration}

        self.action_frequency = self.action_count * (100 / float(self.config.road_length))
        self.avg_time_between_actions = 0 if self.action_count < 2 else \
            self.total_time_between_actions / float(self.action_count - 1)
        self.total_time_without_actions = time_passed if self.start_first_action is None \
            else (self.start_first_action + self.total_time_between_actions + (time_passed - self.time_of_last_action))
