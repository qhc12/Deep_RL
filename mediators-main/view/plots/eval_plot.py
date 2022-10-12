from gym_simulator.evaluation.safety_types import SafetyType
from view.plots.abstract_events_plot import AbstractEventsPlot
from view.colors import get_safety_color


class EvalPlot(AbstractEventsPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)

    @staticmethod
    def grid_height():
        return 1

    def get_grid_height(self):
        return EvalPlot.grid_height()

    def init_plot(self, ax):
        safety_types = [st for st in SafetyType]
        tick_labels = [st.name for st in SafetyType]
        ax.set_ylim(-0.5, len(tick_labels) - 0.5)
        ax.set_yticks(range(len(tick_labels)))
        ax.set_yticklabels(tick_labels)
        ax.set_ylabel('Evaluation', rotation='horizontal', ha='right', va='center')

        for i in range(len(tick_labels)):
            line = ax.hlines(y=[], xmin=0, xmax=0, color=get_safety_color(safety_types[i]), linewidth=5.0)
            self.event_lines.append(line)

    def update_plot(self):
        eval_intervals = self.data.evaluation
        keys = [st for st in SafetyType]
        for i, key in enumerate(keys):
            if key not in eval_intervals:
                continue
            line = self.event_lines[i]
            evaluation = eval_intervals[key]
            self.set_interval_segments(line, evaluation, i)
