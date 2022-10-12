import sys

from gym.utils import seeding
from gym_simulator.roads.event_manager import RoadEventManager
from gym_simulator.roads.max_automation_levels import MaxAutomationLevels
from gym_simulator.roads.road_generator import RoadGenerator


class Road:
    """
    Class defining the Road. Holds all road parts, the current road part, total distance, estimated time, and the
    road events that occur.
    """

    def __init__(self, config, seed, preset_road=None):
        self.config = config
        self.rng, _ = seeding.np_random(seed)
        self.preset_road = preset_road
        # A list of AbstractRoad objects
        self.road_parts = RoadGenerator(self.config, self.rng, preset_road).generate_road()
        self.current_road_part_index = 0  # Index of current road part
        self.current_road_part = self.road_parts[self.current_road_part_index]  # The current road part
        self.total_distance = round(sum(road_part.get_length() for road_part in self.road_parts), 3)
        self.estimated_total_time = round(sum(v.get_travel_time(v.end - v.start) for v in self.road_parts), 2)
        self.last_road_part = self.road_parts[-1]
        self.current_max_level = self.config.maximum_automation_level

        self.event_manager = RoadEventManager(config, self.rng, self.road_parts, self.estimated_total_time, preset_road)
        self.max_automation_levels = MaxAutomationLevels(config, self)

    def step(self, car):
        """
        Updates the current road part and the current maximum level.
        """
        self._update_current_road_part(car.position)
        self.current_max_level = next((level for i, (level, end) in enumerate(self.max_automation_levels.levels) if
                                      end >= car.position and
                                      (i == 0 or car.position > self.max_automation_levels.levels[i - 1][1])),
                                      self.config.maximum_automation_level)
        # Possibly creates a new event
        event_added = self.event_manager.step(car)
        if event_added:
            self.max_automation_levels.update_max_levels()  # Update the maximum automation levels

    def get_target_speed(self):
        """
        Returns the target speed at the current position, which is determined by the current road part (with a speed
        limit) and possible road events which also impact the speed.
        """
        max_event_speed = min((event.max_speed for event in self.event_manager.active_events), default=sys.maxsize)
        return min(max_event_speed, self.current_road_part.speed)

    def _update_current_road_part(self, position):
        if position >= self.current_road_part.end and self.current_road_part_index < len(self.road_parts) - 1:
            self.current_road_part_index = self.current_road_part_index + 1
            self.current_road_part = self.road_parts[self.current_road_part_index]

    def get_road_part(self, position):
        """
        Returns a road part given a position. 
        """
        return next((road_part for road_part in self.road_parts if road_part.start <= position <= road_part.end),
                    self.last_road_part)

    def get_time_to_position(self, current_position, final_position):
        """
        Calculates the time (in seconds) it takes to travel from one position to another on the road, given the speeds
        that are driven on the different roads.
        """

        # If the final position is beyond the end of the road, the time it takes is infinite
        if final_position > self.road_parts[-1].end:
            return sys.maxsize

        speeds = self.max_automation_levels.speeds
        current_speed_index = next(i for i, (_, end) in enumerate(speeds) if
                                   end >= current_position and (i == 0 or current_position > speeds[i - 1][1]))

        total_time = 0
        previous_end = current_position
        for (speed, end) in speeds[current_speed_index:]:
            start = max(current_position, previous_end)
            end = min(final_position, end)
            previous_end = end
            total_time += (float(end - start) / speed) * 3600
            if end > final_position:
                break

        return round(total_time, 2)

    def get_position_in_time(self, current_position, time):
        """
        Calculates the position the car will be in in time seconds.
        """
        # If the final position is beyond the end of the road, the time it takes is infinite
        if current_position > self.road_parts[-1].end:
            return current_position

        speeds = self.max_automation_levels.speeds
        current_speed_index = next(i for i, (_, end) in enumerate(speeds) if
                                   end >= current_position and (i == 0 or current_position > speeds[i - 1][1]))

        for (speed, end) in speeds[current_speed_index:]:
            time_to_end = (float(end - current_position) / speed) * 3600
            if time_to_end > time:
                current_position += (speed * time) / float(3600)
                break
            else:
                current_position = end
                time -= time_to_end

        return current_position
