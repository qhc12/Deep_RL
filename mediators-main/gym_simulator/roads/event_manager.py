from gym_simulator.events.road_events.road_event_generator import RoadEventGenerator


class RoadEventManager:
    """
    Class to handle road events. It generates static events and checks when they become active, and it generates
    and activates dynamic events.
    """

    def __init__(self, config, rng, road_parts, estimated_total_time, preset_road):
        self.road_event_generator = RoadEventGenerator(config, rng, estimated_total_time, preset_road)
        # Static events are generated at the start
        self.events = self.road_event_generator.generate_static_events(road_parts)
        # Events that are currently active
        self.active_events = []
        self.event_index = 0  # The index in the event list from where to start looking for new events

    def step(self, car):
        """
        Updates the active events and possibly creates a new dynamic event. Returns True if a new event has been created,
        False otherwise.
        """
        self.update_active_events(car)
        # Possibly creates a new event
        new_event = self.road_event_generator.generate_next_dynamic_event(
            car, [event.name for event in self.active_events])
        if new_event:
            # Insert new event in list
            index = next((i for i, event in enumerate(self.events) if event.start > new_event.start), len(self.events))
            self.events.insert(index, new_event)
            return True
        return False

    def update_active_events(self, car):
        """
        Updates the list of active events. Events that have passed are removed, and events that are starting now are
        added to the list of active events.
        """
        self.active_events = [event for event in self.active_events if event.end >= car.position]
        for i, event in enumerate(self.events[self.event_index:]):
            if event.start <= car.position <= event.end:
                self.active_events.append(event)
            elif event.start > car.position:
                self.event_index = self.event_index + i
                return
