import sys

from gym_simulator.evaluation.safety_types import SafetyType


class Statistics:
    """
    Class to calculate statistics over several runs of the simulation.
    """

    def __init__(self, config):
        self.config = config
        self.total_runs = 0
        self.runtime = 0.0
        self.total_time_driven = 0.0
        self.avg_driving_time = 0.0

        self.safety_type_active_runs = {}
        self.safety_type_total_events = {}
        self.safety_type_total_events_time = {}
        self.safety_type_avg_event_count = {}
        self.safety_type_avg_time_per_run = {}
        self.safety_type_active_time_ratio = {}
        self.safety_type_shortest_event = {}
        self.safety_type_longest_event = {}
        for st in SafetyType:
            self.safety_type_active_runs[st] = 0
            self.safety_type_total_events[st] = 0
            self.safety_type_total_events_time[st] = 0.0
            self.safety_type_avg_event_count[st] = 0.0
            self.safety_type_avg_time_per_run[st] = 0.0
            self.safety_type_active_time_ratio[st] = 0.0
            self.safety_type_shortest_event[st] = float(sys.maxsize)
            self.safety_type_longest_event[st] = 0.0

        self.aggr_safety_events_per_type = {}

        self.total_action_count = 0  # Total actions over all runs
        self.avg_action_count = 0  # Average action count per run
        self.action_frequency = 0  # Actions per 100 KM
        self.total_time_between_actions = 0.0  # Total time between starts and ends of actions
        self.avg_time_between_actions = 0.0  # Average time between two actions
        self.emergency_stops = 0  # Number of emergency stops made

        self.total_time_driven_in_level = {
            "L0": 0.0,
            "L2": 0.0,
            "L3": 0.0,
            "L4": 0.0
        }
        self.percentage_in_level = {
            "L0": 0.0,
            "L2": 0.0,
            "L3": 0.0,
            "L4": 0.0
        }

        self.runs = []  # List holding information for each individual run

    def update(self, env):
        """
        Updates variables with results of current run.
        """
        evaluation = env.evaluation
        self.total_runs = self.total_runs + 1
        self.total_time_driven = self.total_time_driven + env.time_passed
        for level in self.total_time_driven_in_level.keys():
            self.total_time_driven_in_level[level] = self.total_time_driven_in_level[level] + \
                                                     evaluation.time_driven_in_level[level]

        for st in SafetyType:
            event_count = evaluation.safety_type_event_count[st]
            if event_count > 0:
                self.safety_type_active_runs[st] += 1
                self.safety_type_total_events[st] += event_count
                self.safety_type_total_events_time[st] += evaluation.safety_type_total_event_time[st]
                if evaluation.safety_type_shortest_event[st] < self.safety_type_shortest_event[st]:
                    self.safety_type_shortest_event[st] = evaluation.safety_type_shortest_event[st]
                if evaluation.safety_type_longest_event[st] > self.safety_type_longest_event[st]:
                    self.safety_type_longest_event[st] = evaluation.safety_type_longest_event[st]

        safety_event_types = {}
        for possible_event in env.safety.possible_events:
            name = possible_event.get_name()
            if name in self.aggr_safety_events_per_type:
                aggr = self.aggr_safety_events_per_type[name]
                aggr['Total count'] = aggr['Total count'] + evaluation.safety_type_events_per_name[name]['Count']
                aggr['Total duration'] = \
                    aggr['Total duration'] + evaluation.safety_type_events_per_name[name]['Total duration']
            else:
                self.aggr_safety_events_per_type[name] = {
                    'Total count': evaluation.safety_type_events_per_name[name]['Count'],
                    'Total duration': evaluation.safety_type_events_per_name[name]['Total duration']
                }
            safety_event_types.update({
                "{0} count".format(name): evaluation.safety_type_events_per_name[name]['Count'],
                "{0} duration".format(name): evaluation.safety_type_events_per_name[name]['Total duration']
            })

        self.total_action_count = self.total_action_count + evaluation.action_count
        self.total_time_between_actions = self.total_time_between_actions + evaluation.total_time_between_actions
        if env.evaluation.made_es:
            self.emergency_stops = self.emergency_stops + 1

        single_run_dict = {
            'seed': env.current_seed,
            'Simulation time': env.time_passed,
            'Total time without action': evaluation.total_time_without_actions,
            'Action count': evaluation.action_count,
            'Action frequency': evaluation.action_count * (100 / float(self.config.road_length)),
            'Avg time between actions': 0 if evaluation.action_count <= 1
            else float(evaluation.total_time_between_actions) / (evaluation.action_count - 1)
        }

        for st in SafetyType:
            name = st.name
            active_events = evaluation.safety_type_event_count[st]
            single_run_dict.update({
                'Number of {0} events'.format(name): active_events,
                'Total time in {0} situation'.format(name): evaluation.safety_type_total_event_time[st],
                'Avg duration of {0} situation'.format(name): 0 if active_events == 0
                else evaluation.safety_type_total_event_time[st] / active_events
            })

        self.runs.append(dict(single_run_dict, **safety_event_types))

    def merge(self, other_stats):
        """
        Merge these statistics with different instance of this class.
        """
        self.total_runs += other_stats.total_runs
        self.total_time_driven += other_stats.total_time_driven
        for level in self.total_time_driven_in_level.keys():
            self.total_time_driven_in_level[level] = self.total_time_driven_in_level[level] + \
                                                     other_stats.total_time_driven_in_level[level]

        for st in SafetyType:
            self.safety_type_active_runs[st] += other_stats.safety_type_active_runs[st]
            self.safety_type_total_events[st] += other_stats.safety_type_total_events[st]
            self.safety_type_total_events_time[st] += other_stats.safety_type_total_events_time[st]
            self.safety_type_shortest_event[st] = min(self.safety_type_shortest_event[st],
                                                      other_stats.safety_type_shortest_event[st])
            self.safety_type_longest_event[st] = max(self.safety_type_longest_event[st],
                                                     other_stats.safety_type_longest_event[st])

        for unsafe_event_name in self.aggr_safety_events_per_type.keys():
            aggr = self.aggr_safety_events_per_type[unsafe_event_name]
            other_aggr = other_stats.aggr_safety_events_per_type[unsafe_event_name]
            aggr['Total count'] += other_aggr['Total count']
            aggr['Total duration'] += other_aggr['Total duration']

        self.total_action_count += other_stats.total_action_count
        self.total_time_between_actions += other_stats.total_time_between_actions
        self.emergency_stops += other_stats.emergency_stops

        self.runs.extend(other_stats.runs)

    def finalize(self, runtime):
        """
        Finalizes the calculation of statistics by calculating several averages over all the runs.
        """
        for level in self.percentage_in_level.keys():
            self.percentage_in_level[level] = \
                round((self.total_time_driven_in_level[level] / self.total_time_driven) * 100, 1)

        for st in SafetyType:
            self.safety_type_avg_event_count[st] = float(self.safety_type_total_events[st]) / self.total_runs
            self.safety_type_avg_time_per_run[st] = 0 if self.safety_type_total_events[st] == 0 else \
                float(self.safety_type_total_events_time[st]) / self.safety_type_total_events[st]
            self.safety_type_active_time_ratio[st] = float(self.safety_type_total_events_time[st]) \
                / self.total_time_driven

        self.avg_action_count = float(self.total_action_count) / self.total_runs
        self.action_frequency = self.total_action_count * (100 / float(self.config.road_length * self.total_runs))
        self.avg_time_between_actions = 0 if self.total_action_count <= 1 \
            else float(self.total_time_between_actions) / (self.total_action_count - 1)
        self.runtime = runtime
        self.avg_driving_time = float(self.total_time_driven) / self.total_runs

    def get_dict(self):
        """
        Creates a dictionary from the variables in this class.
        """
        aggr_safety_events_flattened = {}
        for name, values in self.aggr_safety_events_per_type.items():
            aggr_safety_events_flattened["{0} Total count".format(name)] = values['Total count']
            aggr_safety_events_flattened["{0} Total duration".format(name)] = values['Total duration']

        stats_dict = {
            "Total runs": self.total_runs,
            "Runtime": self.runtime,
            "Avg driving time": self.avg_driving_time,
            "Percentage in L0": self.percentage_in_level["L0"],
            "Percentage in L2": self.percentage_in_level["L2"],
            "Percentage in L3": self.percentage_in_level["L3"],
            "Percentage in L4": self.percentage_in_level["L4"],
            "Avg. action count": self.avg_action_count,
            "Action Frequency": self.action_frequency,
            "Avg. time btwn actions": self.avg_time_between_actions,
            "Emergency stops": self.emergency_stops,
        }

        for st in SafetyType:
            name = st.name
            stats_dict.update({
                "{0} runs".format(name): self.safety_type_active_runs[st],
                "Avg {0} events".format(name): self.safety_type_avg_event_count[st],
                "Avg {0} event time".format(name): self.safety_type_avg_time_per_run[st],
                "Shortest {0} event".format(name): self.safety_type_shortest_event[st],
                "Longest {0} event".format(name): self.safety_type_longest_event[st],
                "{0} time ratio".format(name): self.safety_type_active_time_ratio[st]
            })
        stats_dict.update({"runs": self.runs})
        return dict(stats_dict, **aggr_safety_events_flattened)
