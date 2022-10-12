from gym_simulator.evaluation.critical.car_unfit import CarUnfit
from gym_simulator.evaluation.critical.driver_unfit import DriverUnfit
from gym_simulator.evaluation.uncomfortable.double_suggestion import DoubleSuggestion
from gym_simulator.evaluation.misc.pending_request import PendingRequest
from gym_simulator.evaluation.uncomfortable.quick_driver_takeover import QuickTakeover
from gym_simulator.evaluation.uncomfortable.recent_switch import RecentSwitch
from gym_simulator.evaluation.uncomfortable.unnecessary_es import UnnecessaryES


def create_safety_event(event, safety, last_action, pending_action):
    """
    Factory method to create the correct Safety Event.
    """
    if event == CarUnfit:
        return CarUnfit(safety.config, safety.car)
    if event == DriverUnfit:
        return DriverUnfit(safety.config, safety.car, safety.driver)
    if event == UnnecessaryES:
        return UnnecessaryES(safety.config, safety.car, safety.driver, last_action)
    if event == DoubleSuggestion:
        return DoubleSuggestion(safety.config, safety.car, safety.driver, safety.time_passed, last_action)
    if event == PendingRequest:
        return PendingRequest(safety.config, safety.car, safety.driver)
    if event == RecentSwitch:
        return RecentSwitch(safety.config, safety.car, safety.time_passed, safety.time_of_last_switch, last_action)
    if event == QuickTakeover:
        return QuickTakeover(safety.config, safety.car, pending_action)
