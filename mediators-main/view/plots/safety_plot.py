from view.plots.abstract_events_plot import AbstractEventsPlot
from view.colors import get_safety_color


class SafetyPlot(AbstractEventsPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)

    @staticmethod
    def grid_height():
        return 2

    def get_grid_height(self):
        return SafetyPlot.grid_height()

    def init_plot(self, ax):
        tick_labels = []
        for safety_event in self.data.safety_events.keys():
            tick_labels.append(safety_event)
        ax.set_ylim(-0.5, len(tick_labels) - 0.5)
        ax.set_yticks(range(len(tick_labels)))
        ax.set_yticklabels(tick_labels)

        event_intervals = self.get_event_intervals(self.data.safety_events)
        for i, key in enumerate(event_intervals):
            line = ax.hlines(y=[], xmin=0, xmax=0, linewidth=5.0)
            event = event_intervals[key]
            self.set_interval_segments(line, event, i)
            self.event_lines.append(line)

    def update_plot(self):
        event_intervals = self.get_event_intervals(self.data.safety_events)
        for i, key in enumerate(event_intervals):
            line = self.event_lines[i]
            event = event_intervals[key]
            self.set_interval_segments(line, event, i)
            line.set_colors(event["color"])

    def get_event_intervals(self, events):
        safety_event_intervals = {}
        for key in events:
            safety_event_intervals[key] = {"start": [], "end": [], "color": []}
            for safety_event in events[key]:
                safety_event_intervals[key]["start"].append(safety_event.start)
                safety_event_intervals[key]["end"].append(safety_event.end)
                safety_event_intervals[key]["color"].append(get_safety_color(safety_event.type))
        return safety_event_intervals
