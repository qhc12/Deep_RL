from gym_simulator.envs.reward.abstract_reward import AbstractReward
from gym_simulator.evaluation.critical.car_unfit import CarUnfit
from gym_simulator.evaluation.critical.driver_unfit import DriverUnfit
from gym_simulator.evaluation.uncomfortable.double_suggestion import DoubleSuggestion
from gym_simulator.evaluation.uncomfortable.recent_switch import RecentSwitch


class SimpleReward(AbstractReward):
    """
    Very basic Reward class to illustrate its use.
    """

    def __init__(self, env):
        super().__init__(env)

    def get_reward(self):
        """
        Simple reward function:
        - Negative reward when driver is unfit
        - Negative reward when car is unfit
        - Negative reward for each action
        - Positive reward for reaching end of route
        - Negative reward for double suggestion
        - Negative reward for recent switch
        """
        reward = 0
        if self.env.car.position >= self.env.road.total_distance:
            reward += 100
        driver_is_unfit = self.env.safety.safety_event_is_active(DriverUnfit.get_name())
        if driver_is_unfit:
            reward -= 10
        car_is_unfit = self.env.safety.safety_event_is_active(CarUnfit.get_name())
        if car_is_unfit:
            reward -= 10
        double_suggestion = self.env.safety.safety_event_is_active(DoubleSuggestion.get_name())
        if double_suggestion:
            reward -= 10
        recent_switch = self.env.safety.safety_event_is_active(RecentSwitch.get_name())
        if recent_switch:
            reward -= 10
        if self.env.last_action is not None:
            reward -= 50
        return reward
