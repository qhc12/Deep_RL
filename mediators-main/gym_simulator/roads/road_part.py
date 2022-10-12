class RoadPart:
    """
    Road Type. All road types are created using this class.
    """

    def __init__(self, road_type, start, end, max_level, speed=None):
        self.road_type = road_type
        self.start = start
        self.end = end
        self.speed = speed
        self.max_level = max_level

    def get_travel_time(self, distance, current_speed=None):
        """
        Returns the time it takes (in seconds) to travel a given distance on this road type.
        """
        return (float(distance) / (self.speed if current_speed is None or current_speed == 0 else current_speed)) * 3600

    def get_travel_distance(self, time, current_speed=None):
        """
        Returns the distance that is travelled (in KM) on this road type in a given timeframe (in seconds).
        """
        return (time * (self.speed if current_speed is None or current_speed == 0 else current_speed)) / float(3600)

    def get_length(self):
        return self.end - self.start

    def __str__(self):
        return "{0} road from {1} to {2}".format(self.road_type, self.start, self.end)

    def __repr__(self):
        return str(self)
