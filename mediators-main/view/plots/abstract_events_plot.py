from abc import ABC

from view.plots.abstract_plot import AbstractPlot


class AbstractEventsPlot(AbstractPlot, ABC):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)
        self.event_lines = []

    def set_interval_segments(self, line, intervals, i):
        starts = intervals["start"]
        ends = intervals["end"]
        segments = []
        for index in range(len(starts)):
            segment = [[starts[index], i], [ends[index], i]]
            segments.append(segment)
        line.set_segments(segments)

    def get_event_intervals(self, events):
        event_intervals = {}
        for event_key in events:
            event_intervals[event_key] = {"start": [], "end": []}
            for event in events[event_key]:
                event_intervals[event_key]["start"].append(event.start)
                event_intervals[event_key]["end"].append(event.end)
        return event_intervals
