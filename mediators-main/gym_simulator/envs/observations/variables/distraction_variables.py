from gym_simulator.envs.observations.variables.abstract_obs_variables import AbstractObservationVariables


class DistractionVariables(AbstractObservationVariables):
    """
    Class to define observation variables used for a simple distraction use case, to illustrate how different
    variables can be easily defined in a class for different use cases.
    """

    def __init__(self):
        self.max_value = 1000  # Max value for several observation variables (e.g. ttaf)

    def init_obs_bounds(self):
        # Observations used for a simple distraction use case.
        return {
            "distraction": (0, 3),
            "current_level": (0, 3),
            "ttaf_l2": (0, self.max_value),
            "ttaf_l3": (0, self.max_value),
            "ttaf_l4": (0, self.max_value),
            "ttdu": (0, self.max_value),
            "ssl4_declined": (0, 1)
        }

    def get_obs_dict(self, env):
        # Calculation of values for the variables needed for a simple distraction use case.
        ttaf = env.car.get_ttaf()
        last_decline = env.driver.last_decline
        return {
            "distraction": env.driver.distraction,
            "current_level": env.car.current_level,
            # It is ensured that the values for TTAF and TTDU are within the bounds defined
            "ttaf_l2": min(ttaf[0], self.max_value),
            "ttaf_l3": min(ttaf[1], self.max_value),
            "ttaf_l4": min(ttaf[2], self.max_value),
            "ttdu": min(env.driver.ttdu, self.max_value),
            "ssl4_declined": last_decline['L4'] is not None and env.time_passed - last_decline[
                'L4'] < env.config.decline_threshold,  # This boolean value automatically converts to 0 or 1
        }
