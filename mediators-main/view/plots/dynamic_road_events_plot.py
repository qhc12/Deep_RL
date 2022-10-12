from view.plots.abstract_road_events_plot import AbstractRoadEventsPlot


class DynamicRoadEventsPlot(AbstractRoadEventsPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)

    def init_plot(self, ax):
        self.init_road_events_labels(ax, self.config.allowed_dynamic_events, "Dynamic\nevents")
        event_intervals = self.get_event_intervals(self.data.road_events["dynamic"])
        self.init_road_events_lines(ax, event_intervals, self.cp[3])

    def update_plot(self):
        event_intervals = self.get_event_intervals(self.data.road_events["dynamic"])
        self.update_road_lines(event_intervals)
