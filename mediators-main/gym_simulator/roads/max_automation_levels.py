import sys


class MaxAutomationLevels:
    """
    Class keeping track of the maximum automation levels for every part of the road. Also calculates the TTAF and TTAU
    for the different levels based on the max auto levels.
    """

    def __init__(self, config, road):
        self.config = config
        self.timestep = config.timestep
        self.road = road
        # Levels is a sorted list with tuples of the form (<LEVEL>, <END_POSITION>) where LEVEL is the maximum level for
        # that entry, and END_POSITION is where the maximum level ends and switches to the next entry in the list. The
        # list is sorted in ascending order on <END_POSITION>
        self.levels, self.speeds = self.calculate_max_levels()
        self.pessimistic_levels, _ = self.calculate_max_levels("pessimistic_max_level")
        self.optimistic_levels, _ = self.calculate_max_levels("optimistic_max_level")
        self.ttaf = None
        self.ttau = None

    def update_max_levels(self):
        """
        Recalculates the maximum automation levels throughout the road.
        """
        self.levels, self.speeds = self.calculate_max_levels()
        self.pessimistic_levels, _ = self.calculate_max_levels("pessimistic_max_level")
        self.optimistic_levels, _ = self.calculate_max_levels("optimistic_max_level")

    def calculate_max_levels(self, level_type="max_level"):
        """
        Calculates the maximum automation levels throughout the road and returns them in a sorted list of tuples with
        the level and the end position of that level. Also calculates the maximum speeds in a similar fashion.
        """
        levels = []
        speeds = []
        intervals = self.get_event_intervals()  # The intervals on which automation levels might change
        # This is O(n^2), which might not be the quickest possible solution, but there are only a few events so the
        # time it takes is negligible anyway.
        for i in range(len(intervals) - 1):  # Loop through the intervals
            start = intervals[i]
            end = intervals[i + 1]
            lowest_level = self.config.maximum_automation_level
            lowest_speed = sys.maxsize
            # Loop through the events to see which ones overlap with the current interval
            for event_index, event in enumerate(self.road.event_manager.events):
                # Events are sorted on starting position, so from the first event that starts after the current interval
                # end, all other events after it will also be outside the interval
                if event.start >= end:
                    break
                # If the event ends after the start of the interval, it must be in the interval range because of the
                # previous if clause (its start is before the end of the interval). So if then the max level of the
                # event is lower than the current lowest level for this interval, update it
                elif event.end > start:
                    if getattr(event, level_type) < lowest_level:
                        lowest_level = getattr(event, level_type)
                    if event.max_speed < lowest_speed:
                        lowest_speed = event.max_speed

            # Get the current road part and take the minimum level for that road part
            current_road_part = self.road.get_road_part(end - 0.01)
            lowest_level = min(lowest_level, current_road_part.max_level)
            lowest_speed = min(lowest_speed, current_road_part.speed)
            # If the previous level had the same lowest level, simply extend it
            if len(levels) > 0 and levels[-1][0] == lowest_level:
                levels[-1] = (lowest_level, end)
            else:
                levels.append((lowest_level, end))
            if len(speeds) > 0 and speeds[-1][0] == lowest_speed:
                speeds[-1] = (lowest_speed, end)
            else:
                speeds.append((lowest_speed, end))
        return levels, speeds

    def get_event_intervals(self):
        """
        Returns a sorted list with every point in the road in which the maximum automation level might change, which
        equals every start and end of an event and the end of the road.
        """
        start_and_end_times = {0}
        road_length = self.road.total_distance
        for event in self.road.event_manager.events:
            start_and_end_times.add(min(event.start, road_length))
            start_and_end_times.add(min(event.end, road_length))
        for road_part in self.road.road_parts:
            start_and_end_times.add(road_part.start)
            start_and_end_times.add(road_part.end)
        start_and_end_times.add(self.road.total_distance)
        return sorted(list(start_and_end_times))

    def get_ttaf(self, position, level_type="levels"):
        """
        Returns TTAF for L2, L3, and L4 in a list of length 3, in that respective order
        """
        levels = getattr(self, level_type)
        self.ttaf = self._get_time_to_max_levels(position, levels)
        return self.ttaf

    def _get_time_to_max_levels(self, position, levels):
        """
        Calculates the time it takes for the car before it reaches the various maximum automation levels.
        """
        # If the car has driven the complete route, keep the ttaf the same as the last level it was on
        if position > self.road.last_road_part.end:
            return self.ttaf

        index = self.get_index_of_current_level(position, levels)  # Index of current position in levels list
        current_level = levels[index][0]  # Current max level

        if current_level == "L4":  # In this case, all automation levels are currently available
            return [0, 0, 0]
        elif current_level == "L3":  # In this case, L3 and L2 are currently available. L4 needs to be calculated.
            l4_starts_at = self.get_start_of_next_level("L4", index, levels)
            return [0, 0, self.road.get_time_to_position(position, l4_starts_at)]
        elif current_level == "L2":  # In this case, L2 is currently available. L3 and L4 need to be calculated.
            l4_starts_at = self.get_start_of_next_level("L4", index, levels)
            l3_starts_at = self.get_start_of_next_level("L3", index, levels)
            if l3_starts_at > l4_starts_at:  # If L4 is available before L3, then L3 is available at the moment L4 is
                # Use time to L4 fitness for both L3 and L4
                time_to_l4 = self.road.get_time_to_position(position, l4_starts_at)
                return [0, time_to_l4, time_to_l4]
            else:  # Else, both L4 and L3 need to be calculated separately
                return [0, self.road.get_time_to_position(position, l3_starts_at),
                        self.road.get_time_to_position(position, l4_starts_at)]
        else:  # In the last case, L4, L3 and L2 all need to be calculated
            l4_starts_at = self.get_start_of_next_level("L4", index, levels)
            l3_starts_at = self.get_start_of_next_level("L3", index, levels)
            l2_starts_at = self.get_start_of_next_level("L2", index, levels)

            time_to_l4 = self.road.get_time_to_position(position, l4_starts_at)
            if l4_starts_at < l3_starts_at:  # Same logic as above
                # Time to L3 is the same as time to L4
                time_to_l3 = time_to_l4
            else:
                time_to_l3 = self.road.get_time_to_position(position, l3_starts_at)

            if l4_starts_at < l2_starts_at:
                time_to_l2 = time_to_l4
            elif l3_starts_at < l2_starts_at:
                time_to_l2 = time_to_l3
            else:
                time_to_l2 = self.road.get_time_to_position(position, l2_starts_at)

            return [time_to_l2, time_to_l3, time_to_l4]

    def get_ttau(self, position, level_type="levels"):
        """
        Returns TTAU for L2, L3, and L4 in a list of length 3, in that respective order.
        """
        levels = getattr(self, level_type)
        self.ttau = self._get_time_to_end_of_levels(position, levels)
        return self.ttau

    def _get_time_to_end_of_levels(self, position, levels):
        # If the car has driven the complete route, keep the ttau the same as the last level it was on
        if position > self.road.last_road_part.end:
            return self.ttau

        index = self.get_index_of_current_level(position, levels)  # Index of current position in levels list
        current_level = levels[index][0]  # Current max level

        if current_level == "L0":  # If max level is L0, all levels are currently unavailable
            return [0, 0, 0]
        elif current_level == "L2":  # In this case, L3 and L4 are unavailable and L2 needs to be calculated
            l2_ends_at = self.get_start_of_next_level("L0", index, levels)
            return [self.road.get_time_to_position(position, l2_ends_at), 0, 0]
        elif current_level == "L3":  # L4 unavailable, L3 and L2 need to be calculated
            l2_ends_at = self.get_start_of_next_level("L0", index, levels)
            l3_ends_at = self.get_start_of_next_level("L2", index, levels)
            # If L2 ends (meaning it is not available anymore) before L3, their TTAU is the same
            if l2_ends_at < l3_ends_at:
                time_to_l0 = self.road.get_time_to_position(position, l2_ends_at)
                return [time_to_l0, time_to_l0, 0]
            else:
                return [self.road.get_time_to_position(position, l2_ends_at),
                        self.road.get_time_to_position(position, l3_ends_at), 0]
        else:
            l2_ends_at = self.get_start_of_next_level("L0", index, levels)
            l3_ends_at = min(self.get_start_of_next_level("L2", index, levels), l2_ends_at)
            l4_ends_at = min(self.get_start_of_next_level("L3", index, levels), l3_ends_at)
            time_to_l0 = self.road.get_time_to_position(position, l2_ends_at)
            if l2_ends_at == l3_ends_at:
                time_l3_ends = time_to_l0
            else:
                time_l3_ends = self.road.get_time_to_position(position, l3_ends_at)
            if l3_ends_at == l4_ends_at:
                time_l4_ends = time_l3_ends
            else:
                time_l4_ends = self.road.get_time_to_position(position, l4_ends_at)
            return [time_to_l0, time_l3_ends, time_l4_ends]

    def get_index_of_current_level(self, position, levels=None):
        """
        Returns the index in the list of levels given the current position (i.e. the index of the maximum automation
        level that is available at this point). If the car is past the end of the road, the index of the last level
        is returned.
        """
        if levels is None:
            levels = self.levels
        return next((i for i, level in enumerate(levels) if position < level[1] and
                    (i == 0 or position >= levels[i - 1][1])), len(levels) - 1)

    def get_start_of_next_level(self, level, current_level_index, levels=None):
        """
        Gets the starting position of the first occurrence of a given level in the list of levels after a given index.
        If the level does not occur anymore, return sys.maxsize.
        """
        if levels is None:
            levels = self.levels
        remaining_levels = levels[current_level_index:]
        return next((remaining_levels[i - 1][1] for i, v in enumerate(remaining_levels) if v[0] == level), sys.maxsize)
