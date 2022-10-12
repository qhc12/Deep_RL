from view.plots.abstract_events_plot import AbstractEventsPlot


class ComfortPlot(AbstractEventsPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)

    @staticmethod
    def grid_height():
        return 2

    def get_grid_height(self):
        return ComfortPlot.grid_height()

    def init_plot(self, ax):
        tick_labels = []
        for comfort_event in self.data.comfort_events.keys():
            tick_labels.append(comfort_event)
        ax.set_ylim(-0.5, len(tick_labels) - 0.5)
        ax.set_yticks(range(len(tick_labels)))
        ax.set_yticklabels(tick_labels)

        event_intervals = self.get_event_intervals(self.data.comfort_events)
        for i, key in enumerate(event_intervals):
            line = ax.hlines(y=[], xmin=0, xmax=0, color='r', linewidth=5.0)
            event = event_intervals[key]
            self.set_interval_segments(line, event, i)
            self.event_lines.append(line)

    def update_plot(self):
        event_intervals = self.get_event_intervals(self.data.comfort_events)
        for i, key in enumerate(event_intervals):
            line = self.event_lines[i]
            event = event_intervals[key]
            self.set_interval_segments(line, event, i)
