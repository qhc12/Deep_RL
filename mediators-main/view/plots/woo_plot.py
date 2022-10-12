from view.plots.abstract_events_plot import AbstractEventsPlot
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe


class WOOPlot(AbstractEventsPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)

    @staticmethod
    def grid_height():
        return 5

    def get_grid_height(self):
        return WOOPlot.grid_height()

    def init_plot(self, ax):
        tick_labels = [label for label in self.config.available_actions if not (label == 'DN' or label == 'CANCEL')]
        ax.set_ylim(-0.5, len(tick_labels) - 0.5)
        ax.set_yticks(range(len(tick_labels)))
        ax.set_yticklabels(tick_labels)
        ax.set_ylabel('WOO Actions', rotation='horizontal', ha='right', va='center')
        woo_label = mpatches.Patch(color=self.cp[2], label='Window of Opportunity')
        ax.legend(handles=[woo_label])

        for i in range(len(tick_labels)):
            line = ax.hlines(y=[], xmin=0, xmax=0, linewidth=5.0, color=self.cp[2],
                             path_effects=[pe.Stroke(linewidth=10.0, foreground='black'), pe.Normal()])
            # line = ax.hlines(y=[], xmin=0, xmax=0, color='r', linewidth=10.0)
            self.event_lines.append(line)

    def update_plot(self):
        action_intervals = self.get_event_intervals(self.data.actions)
        keys = [label for label in self.config.available_actions if not (label == 'DN' or label == 'CANCEL')]
        for i, key in enumerate(keys):
            if key not in action_intervals:
                continue
            line = self.event_lines[i]
            action = action_intervals[key]
            self.set_interval_segments(line, action, i)
            # line.set_colors(action["color"])

    def get_event_intervals(self, events):
        action_intervals = {}
        for action_key in events:
            action_intervals[action_key] = {"start": [], "end": []}
            for action in events[action_key]:
                action_intervals[action_key]["start"].append(action.earliest_start)
                action_intervals[action_key]["end"].append(action.latest_start)
        return action_intervals
