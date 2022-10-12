from gym_simulator.roads.road_part import RoadPart


class RoadGenerator:
    """
    Class to randomly generate roads.
    """

    def __init__(self, config, rng, preset_road=None):
        self.config = config
        self.rng = rng
        self.preset_road = preset_road

    def generate_road(self):
        """
        Generate a random road with the available road types and road length defined in the config file.
        Every road starts and ends with a city road. The road parts in between are random, but different
        road parts have different maximum number of occurrences, defined in config file (e.g. highway can only occur
        once). Also, road parts have different minimum and maximum lengths.

        If a preset road is defined, use this instead.
        """
        if self.preset_road is not None and self.preset_road.includes_road():
            road_parts = []
            last_end = 0.0
            for road_part in self.preset_road.road:
                road_type = road_part[0]
                road_length = road_part[1]
                road_speed = road_part[2] if len(road_part) == 3 else \
                    self.config.allowed_road_types[road_type]["speed_limit"]
                road_parts.append(self.__create_road_part(road_type, last_end, length=road_length, speed=road_speed))
                last_end = last_end + road_length
            return road_parts

        length = self.config.road_length
        allowed_road_types = self.config.allowed_road_types
        min_city_length = allowed_road_types["city"]["min_length"]
        road_types_count = {}
        for road_type in self.config.allowed_road_types.keys():
            road_types_count[road_type] = 0

        if "city" not in allowed_road_types:
            raise ValueError('Currently, every road should always contain City road.')

        # Always start with urban road
        road_parts = [self.__create_road_part("city", 0.0, remaining_distance=length)]
        road_types_count["city"] = 1

        # Create random alternating road parts
        remaining_distance = length - road_parts[-1].end
        while remaining_distance > min_city_length:
            last_road_part = road_parts[-1]
            # Road type is available if it is allowed (in config file), it is not the same as the previous road_type,
            # its minimum length is smaller than the remaining distance minus the minimum length of urban road
            # (because this always ends) and its usage count does not exceed the maximum
            available_road_types = [road_type for road_type in allowed_road_types.keys()
                                    if not road_type == last_road_part.road_type
                                    and remaining_distance - min_city_length >
                                    allowed_road_types[road_type]["min_length"]
                                    and not road_type == "highway_link"
                                    and road_types_count[road_type] < allowed_road_types[road_type]["max_occurrences"]]
            # If no road types are available anymore, stop
            if len(available_road_types) == 0:
                break
            # Choose a random road type from the available ones
            next_road_type = self.rng.choice(available_road_types)
            road_types_count[next_road_type] += 1
            road_part = self.__create_road_part(next_road_type, road_parts[-1].end,
                                                remaining_distance=remaining_distance - min_city_length)
            if next_road_type == "highway" and "highway_link" in allowed_road_types:
                enter_highway = self.__create_road_part("highway_link", last_road_part.end,
                                                        remaining_distance=remaining_distance - min_city_length)
                road_part.start = enter_highway.end
                exit_highway = self.__create_road_part("highway_link", road_part.end,
                                                       remaining_distance=remaining_distance - min_city_length)
                length_exit = exit_highway.end - exit_highway.start
                exit_highway.end = exit_highway.start
                exit_highway.start = exit_highway.end - length_exit
                road_part.end = exit_highway.start
                road_parts.append(enter_highway)
                road_parts.append(road_part)
                road_parts.append(exit_highway)
            else:
                road_parts.append(road_part)
            remaining_distance = length - road_parts[-1].end

        # End with urban road
        last_road_part = road_parts[-1]
        if last_road_part.road_type == "city":
            last_road_part.end = length
        else:
            start = last_road_part.end
            road_parts.append(self.__create_road_part("city", start, length - start))
        return road_parts

    def __create_road_part(self, road_type, start, length=None, remaining_distance=None, speed=None):
        road_part = self.config.allowed_road_types[road_type]
        min_length = road_part["min_length"]
        max_length = road_part["max_length"]
        max_level = road_part["max_level"]
        if speed is None:
            speed = road_part["speed_limit"]
        if length is None:
            length = self.__get_random_length(min_length, max_length, remaining_distance)
        return RoadPart(road_type, round(start, 3), round(start + length, 3), max_level, speed)

    def __get_random_length(self, min_length, max_length, remaining_distance):
        return round(self.rng.uniform(min_length, min(max_length, remaining_distance)), 1)
