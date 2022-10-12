from view.plots.actions_plot import ActionsPlot
from view.plots.actions_single_line_plot import ActionsSingleLinePlot
from view.plots.driver_events_plot import DriverEventsPlot
from view.plots.driver_plot import DriverPlot
from view.plots.dynamic_road_events_plot import DynamicRoadEventsPlot
from view.plots.eval_plot import EvalPlot
from view.plots.future_actions_plot import FutureActionsPlot
from view.plots.levels_plot import LevelsPlot
from view.plots.safety_plot import SafetyPlot
from view.plots.speed_plot import SpeedPlot
from view.plots.static_road_events_plot import StaticRoadEventsPlot
from view.plots.time_driven_plot import TimeDrivenPlot
from view.plots.ttaf_plot import TTAFPlot
from view.plots.ttau_plot import TTAUPlot
from view.plots.ttdf_plot import TTDFPlot
from view.plots.ttdu_plot import TTDUPlot
from view.plots.woo_plot import WOOPlot


def map_view(view):
    """
    Map view string (specified in the view yaml file) to corresponding plot.
    """
    if view == "ROAD":
        return LevelsPlot
    if view == "ACTIONS":
        return ActionsPlot
    if view == "ACTIONS_SINGLE_LINE":
        return ActionsSingleLinePlot
    if view == "FUTURE_ACTIONS":
        return FutureActionsPlot
    if view == "WOO":
        return WOOPlot
    if view == "STATIC_EVENTS":
        return StaticRoadEventsPlot
    if view == "DYNAMIC_EVENTS":
        return DynamicRoadEventsPlot
    if view == "TTAF":
        return TTAFPlot
    if view == "TTAU":
        return TTAUPlot
    if view == "DRIVER_EVENTS":
        return DriverEventsPlot
    if view == "DRIVER_STATE":
        return DriverPlot
    if view == "TTDU":
        return TTDUPlot
    if view == "TTDF":
        return TTDFPlot
    if view == "EVALUATION":
        return EvalPlot
    if view == "DETAILED_EVALUATION":
        return SafetyPlot
    if view == "TIME_DRIVEN":
        return TimeDrivenPlot
    if view == "SPEED":
        return SpeedPlot
    return None
