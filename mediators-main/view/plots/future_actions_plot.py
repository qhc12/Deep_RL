from view.plots.abstract_events_plot import AbstractEventsPlot
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe


class FutureActionsPlot(AbstractEventsPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)

    @staticmethod
    def grid_height():
        return 2

    def get_grid_height(self):
        return FutureActionsPlot.grid_height()

    def init_plot(self, ax):
        tick_labels = [label for label in self.config.available_actions if (label.startswith('SSL') or
                                                                            label.startswith('ESL'))]
        ax.set_ylim(-0.5, len(tick_labels) - 0.5)
        ax.set_yticks(range(len(tick_labels)))
        ax.set_yticklabels(tick_labels)
        ax.set_ylabel('Future Actions', rotation='horizontal', ha='right', va='center')

        for i in range(len(tick_labels)):
            line = ax.hlines(y=[], xmin=0, xmax=0, linewidth=5.0,
                             path_effects=[pe.Stroke(linewidth=10.0, foreground='black'), pe.Normal()])
            self.event_lines.append(line)

    def update_plot(self):
        action_intervals = self.get_event_intervals(self.data.future_actions)
        keys = [label for label in self.config.available_actions if (label.startswith('SSL') or
                                                                     label.startswith('ESL'))]
        for i, key in enumerate(keys):
            if key not in action_intervals:
                continue
            line = self.event_lines[i]
            action = action_intervals[key]
            self.set_interval_segments(line, action, i)
            line.set_colors(action["color"])

    def get_event_intervals(self, events):
        action_intervals = {}
        for action_key in events:
            action_intervals[action_key] = {"start": [], "end": [], "color": []}
            for action in events[action_key]:
                action_intervals[action_key]["start"].append(action.start)
                action_intervals[action_key]["end"].append(action.end)
                if action.is_pending():
                    color = self.cp[0]
                elif action.is_successful():
                    color = self.cp[2]
                else:
                    color = self.cp[1]
                action_intervals[action_key]["color"].append(color)
        return action_intervals
