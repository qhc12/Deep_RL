from abc import ABC

from view.plots.abstract_events_plot import AbstractEventsPlot


class AbstractRoadEventsPlot(AbstractEventsPlot, ABC):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)

    @staticmethod
    def grid_height():
        return 1

    def get_grid_height(self):
        return AbstractRoadEventsPlot.grid_height()

    def init_road_events_labels(self, ax, allowed_events, ylabel):
        tick_labels = []
        for allowed_event in allowed_events:
            tick_labels.append(allowed_event)
        ax.set_ylim(-0.5, max(len(tick_labels) - 0.5, 0.5))
        ax.set_yticks(range(len(tick_labels)))
        ax.set_yticklabels(tick_labels)
        ax.set_ylabel(ylabel, rotation='horizontal', ha='right', va='center')

    def init_road_events_lines(self, ax, event_intervals, color):
        for i, key in enumerate(event_intervals):
            line = ax.hlines(y=[], xmin=0, xmax=0, color=color, linewidth=5.0)
            event = event_intervals[key]
            self.set_interval_segments(line, event, i)
            self.event_lines.append(line)

    def update_road_lines(self, event_intervals):
        for i, key in enumerate(event_intervals):
            line = self.event_lines[i]
            event = event_intervals[key]
            self.set_interval_segments(line, event, i)
