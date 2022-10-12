from gym_simulator.config.enums_to_classes_mapping import map_driver_event_to_class
from gym_simulator.utils.utils import calculate_probability_per_timestep


class DriverEventGenerator:
    """
    Class to randomly generate driver events.
    """

    def __init__(self, config, rng, estimated_total_time):
        self.config = config
        self.rng = rng
        self.allowed_events = self._map_possible_driver_events()  # A list of allowed event classes
        self.event_counts = [0] * len(self.allowed_events)  # Keeps track of how often each event has happened already
        self.event_probs_per_timestep = []
        # For each driver event, calculate the probability of it happening in each timestep, based on the overall
        # probabilities defined in the config file and the estimated total driving time
        for prob in self.config.driver_event_probability:
            self.event_probs_per_timestep.append(calculate_probability_per_timestep(
                estimated_total_time / self.config.timestep, prob))

    def generate_next_event(self, car, pending_events):
        """
        Possibly generates a driver event (with some probability).

        If an event is created, the initialized event is returned, else the function returns None.
        """
        for i, event in enumerate(self.allowed_events):
            # The event should not exceed the maximum allowed number of times it is allowed to occur. Also, no event
            # of the same type should already be pending (e.g. you cannot have 2 simultaneous distraction events)
            if self.event_counts[i] < self.config.max_occurrences_of_driver_event[i] and \
                    not any(isinstance(ev, event) for ev in pending_events):
                if self.rng.rand() < self.event_probs_per_timestep[i]:
                    # Create a new event
                    self.event_counts[i] = self.event_counts[i] + 1
                    evt = event(self.config, self.rng, car.position)
                    if evt.is_possible(car.current_level):
                        return evt
        return None

    def _map_possible_driver_events(self):
        """
        Returns a list of driver event classes that are allowed.
        """
        allowed_events = []
        for allowed_event in self.config.allowed_driver_events:
            allowed_events.append(map_driver_event_to_class(allowed_event))
        return allowed_events
