from view.plots.abstract_events_plot import AbstractEventsPlot


class DriverEventsPlot(AbstractEventsPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)

    @staticmethod
    def grid_height():
        return 1

    def get_grid_height(self):
        return DriverEventsPlot.grid_height()

    def init_plot(self, ax):
        tick_labels = []
        for allowed_event in self.config.allowed_driver_events:
            tick_labels.append(allowed_event.name)
        ax.set_ylim(-0.5, len(tick_labels) - 0.5)
        ax.set_yticks(range(len(tick_labels)))
        ax.set_yticklabels(tick_labels)

        event_intervals = self.get_event_intervals(self.data.driver_events)
        for i, key in enumerate(event_intervals):
            line = ax.hlines(y=[], xmin=0, xmax=0, color='r', linewidth=5.0)
            event = event_intervals[key]
            self.set_interval_segments(line, event, i)
            self.event_lines.append(line)

    def update_plot(self):
        event_intervals = self.get_event_intervals(self.data.driver_events)
        for i, key in enumerate(event_intervals):
            line = self.event_lines[i]
            event = event_intervals[key]
            self.set_interval_segments(line, event, i)
