from gym_simulator.config.allowed_values import RoadEventType
from gym_simulator.events.road_events.road_event import RoadEvent
from gym_simulator.utils.utils import calculate_probability_per_timestep


class RoadEventGenerator:
    """
    Class to generate both dynamic and static road events (randomly).
    """

    def __init__(self, config, rng, estimated_total_time, preset_road=None):
        """
        estimated_total_time is an estimation (in seconds) of the total time the drive will take.
        preset_road is an optional argument. If defined, it contains a preset road with possible static and dynamic
            events.
        """
        self.config = config
        self.rng = rng
        self.dynamic_event_counts = {}
        self.dynamic_prob_per_timestep = {}
        for event_name, event in self.config.allowed_dynamic_events.items():
            self.dynamic_event_counts[event_name] = 0
            self.dynamic_prob_per_timestep[event_name] = \
                calculate_probability_per_timestep(estimated_total_time / self.config.timestep,
                                                   event["probability"])

        # If there is a preset road it might include dynamic (and static) events. In that case, these (predefined)
        # events are used instead of randomly generating them.
        self.preset_road = preset_road
        self.preset_dynamic_events = []
        self.dynamic_events_iter = None
        self.next_dynamic_event = None
        if self.preset_road is not None and self.preset_road.includes_dynamic_events():
            for dynamic_event in self.preset_road.dynamic_events:
                event_name = dynamic_event[0]
                if event_name in self.config.allowed_dynamic_events:
                    event_start = dynamic_event[1]
                    event_end = dynamic_event[2]
                    default_level = self.config.allowed_dynamic_events[event_name]["default_level"]
                    default_speed = self.config.allowed_dynamic_events[event_name]["default_speed"]
                    self.preset_dynamic_events.append(RoadEvent(event_name, RoadEventType.DYNAMIC, event_start,
                                                                event_end, default_level, default_speed))
            self.preset_dynamic_events.sort(key=lambda ev: ev.start)
            self.dynamic_events_iter = iter(self.preset_dynamic_events)
            self.next_dynamic_event = next(self.dynamic_events_iter, None)

    def generate_static_events(self, road_parts):
        """
        Randomly generates static events for the different road parts. If a predefined road is used and it contains
        static events, these are used instead.
        """
        static_events = []
        # Possibly use predefined static events
        if self.preset_road is not None and self.preset_road.includes_static_events():
            for static_event in self.preset_road.static_events:
                event_name = static_event[0]
                if event_name in self.config.allowed_static_events:
                    event_start = static_event[1]
                    event_end = static_event[2]
                    default_level = self.config.allowed_static_events[event_name]["default_level"]
                    default_speed = self.config.allowed_static_events[event_name]["default_speed"]
                    static_events.append(RoadEvent(event_name, RoadEventType.STATIC, event_start, event_end,
                                                   default_level, default_speed))
            return sorted(static_events, key=lambda ev: ev.start)

        # If static events are not predefined, randomly generate them (one per road part currently), none on the highway
        for road_part in road_parts[:-1]:
            if not (road_part.road_type == "Highway" or road_part.road_type == "Highway Link"):
                for event_name, event in self.config.allowed_static_events.items():
                    if self.rng.rand() < event["probability"]:
                        event_start = self.rng.uniform(road_part.start, road_part.end - event["max_length"])
                        event_end = min(self.rng.uniform(event_start + event["min_length"],
                                                         event_start + event["max_length"]), road_part.end)
                        static_events.append(RoadEvent(event_name, RoadEventType.STATIC, event_start, event_end,
                                                       event["default_level"], event["default_speed"]))
        return sorted(static_events, key=lambda ev: ev.start)

    def generate_next_dynamic_event(self, car, active_events=None):
        """
        Possibly generates a dynamic event. Returns None if no dynamic event is generated.
        """
        # This specifies how far ahead an event is known, which is a random number within predefined bounds
        lookahead_distance = self.rng.uniform(self.config.dynamic_event_min_lookahead,
                                              self.config.dynamic_event_max_lookahead)

        # If dynamic events are predefined, use these
        if self.preset_road is not None and self.preset_road.includes_dynamic_events():
            if self.next_dynamic_event is not None and \
                    self.next_dynamic_event.start <= car.position + lookahead_distance:
                event_to_return = self.next_dynamic_event
                self.next_dynamic_event = next(self.dynamic_events_iter, None)
                return event_to_return
            return None

        # If not predefined, randomly generate a dynamic event (or not, then None is returned)
        for event_name, event in self.config.allowed_dynamic_events.items():
            # Check if dynamic count does not exceed maximum dynamic event count yet
            if self.dynamic_event_counts[event_name] < event["max_occurrences"] and \
                    (active_events is None or event_name not in active_events):
                if self.rng.rand() < self.dynamic_prob_per_timestep[event_name]:
                    self.dynamic_event_counts[event_name] += 1
                    start = car.position + lookahead_distance
                    end = start + self.rng.uniform(event["min_length"], event["max_length"])
                    return RoadEvent(event_name, RoadEventType.DYNAMIC, start, end, event["default_level"],
                                     event["default_speed"])
        return None
