from gym.utils import seeding


class Car:
    """
    Car class, which handles any environment variables related to the Car.
    """

    def __init__(self, config, seed, road):
        """
        Initialize the car class with the config settings, a seed from which a random number generator is created, and
        the road class such that the car knows on which road it is driving.
        """
        self.config = config
        self.rng, _ = seeding.np_random(seed)
        self.road = road
        self.position = 0.0  # Starting position
        self.speed = 0.0  # Initial speed
        self.current_level = config.initial_level  # Initial automation level
        self.timestamp = 0.0  # Initial time

    def step(self, timestamp):
        """
        Updates speed and position of car.
        """
        self.timestamp = timestamp
        # If road data is used, speed and position are taken from there
        if self.road.preset_road is not None and self.road.preset_road.includes_route_data():
            self.speed = self.road.preset_road.route_data[timestamp]['speed']
            self.position = round(self.road.preset_road.route_data[timestamp]['position'] / 1000, 5)
        # Otherwise, speed is calculated based on current speed and some randomness, and position is updated based on
        # speed
        else:
            self.speed = self.calculate_speed()
            self.position = round(self.position + (self.speed / (3600.0 / self.config.timestep)), 5)

    def get_ttaf(self, level_type="levels", position=None):
        """
        Calculates the TTAF of the car.
        Default option for level_type is "levels", this uses realistic values for available automation levels based on
        static and dynamic road events and road types.
        Other options are:
        - "pessimistic_levels": using pessimistic values for available automation levels.
        - "optimistic_levels": using optimistic values for available automation levels.

        position: if it's not set, the current position of the car is used to calculate TTAF from. Else, the specified
        position is used.
        """
        # Calculate TTAF
        ttaf = self.road.max_automation_levels.get_ttaf(position if position else self.position, level_type)
        # If road data is used and use_parsed_tta_for_actions is True, TTAF for L2 is taken from road data.
        if self.config.use_parsed_tta_for_actions and self.road.preset_road is not None and \
                self.road.preset_road.includes_route_data() and level_type == "levels":
            ttaf[0] = self.road.preset_road.route_data[self.timestamp]['ttaf']
        return ttaf

    def get_parsed_ttaf_l2(self):
        if self.road.preset_road is not None and self.road.preset_road.includes_route_data():
            return self.road.preset_road.route_data[self.timestamp]['ttaf']
        return None

    def get_ttau(self, level_type="levels", position=None):
        """
        Calculates the TTAU of the car.
        Default option for level_type is "levels", this uses realistic values for available automation levels based on
        static and dynamic road events and road types.
        Other options are:
        - "pessimistic_levels": using pessimistic values for available automation levels.
        - "optimistic_levels": using optimistic values for available automation levels.

        position: if it's not set, the current position of the car is used to calculate TTAU from. Else, the specified
        position is used.
        """
        # Calculate TTAU
        ttau = self.road.max_automation_levels.get_ttau(position if position else self.position, level_type)
        # If road data is used and use_parsed_tta_for_actions is True, TTAU for L2 is taken from road data.
        if self.config.use_parsed_tta_for_actions and self.road.preset_road is not None and \
                self.road.preset_road.includes_route_data() and level_type == "levels":
            ttau[0] = self.road.preset_road.route_data[self.timestamp]['ttau']
        return ttau

    def get_parsed_ttau_l2(self):
        if self.road.preset_road is not None and self.road.preset_road.includes_route_data():
            return self.road.preset_road.route_data[self.timestamp]['ttau']
        return None

    def calculate_speed(self):
        """
        Function to calculate the current speed based on the acceleration and the previous speed.
        """
        return self.speed + (self._get_acceleration() * self.config.timestep * 3.6)

    def _get_acceleration(self):
        """
        Function to calculate acceleration in current timestep, based on current road, current speed, acceleration
        settings, and randomness.
        """
        target_speed = self.road.get_target_speed()
        current_speed = self.speed
        # If the target speed cannot be reached within one timestep with full acceleration, acceleration should be full
        if target_speed - (current_speed + (self.config.acc_coefficient * self.config.timestep * 3.6)) > \
                self.config.speed_tolerance:
            return self.config.acc_coefficient
        # If the target speed cannot be reached within one timestep with full negative acceleration, acceleration should
        # be fully negative
        elif (current_speed - (self.config.acc_coefficient * self.config.timestep * 3.6)) - target_speed > \
                self.config.speed_tolerance:
            return -self.config.acc_coefficient
        # When the speed is within range target_speed +/- speed_tolerance, only change speed with a small probability
        elif (self.current_level > "L0" and self.rng.rand() < 0.01) or \
                (self.current_level == "L0" and self.rng.rand() < 0.02):
            if current_speed <= target_speed:
                # If current speed is smaller than target speed, we accelerate
                max_speed_increase = target_speed + self.config.speed_tolerance - current_speed
                max_acceleration = min((max_speed_increase / 3.6) / self.config.timestep, self.config.acc_coefficient)
                return self.rng.rand() * max_acceleration
            else:
                # If current speed is greater than target speed, we decelerate
                max_speed_decrease = current_speed - (target_speed - self.config.speed_tolerance)
                max_deceleration = max((-max_speed_decrease / 3.6) / self.config.timestep, -self.config.acc_coefficient)
                return self.rng.rand() * max_deceleration
        else:
            return 0
