from view.plots.abstract_events_plot import AbstractEventsPlot
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe


class ActionsSingleLinePlot(AbstractEventsPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)
        self.actions_line = None

    @staticmethod
    def grid_height():
        return 2

    def get_grid_height(self):
        return ActionsSingleLinePlot.grid_height()

    def init_plot(self, ax):
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([0])
        ax.set_yticklabels(["Action"])
        # ax.set_ylabel('Actions', rotation='horizontal', ha='right', va='center')
        ssl = mpatches.Patch(color=self.__map_colors('SSL'), label='SSL')
        esl = mpatches.Patch(color=self.__map_colors('ESL'), label='ESL')
        cd = mpatches.Patch(color=self.__map_colors('CD'), label='CD')
        es = mpatches.Patch(color=self.__map_colors('ES'), label='ES')
        cr = mpatches.Patch(color=self.__map_colors('CR'), label='CR')
        cf = mpatches.Patch(color=self.__map_colors('CF'), label='CF')
        pd = mpatches.Patch(color=self.__map_colors('PD'), label='PD')
        ax.legend(handles=[ssl, esl, cd, es, cr, cf, pd], ncol=7)

        self.actions_line = ax.hlines(y=[], xmin=0, xmax=0, linewidth=5.0,
                                      path_effects=[pe.Stroke(linewidth=10.0, foreground='black'), pe.Normal()])

    def update_plot(self):
        action_intervals = self.get_event_intervals(self.data.actions)
        self.set_interval_segments(self.actions_line, action_intervals, 0)
        self.actions_line.set_colors(action_intervals["color"])

    def get_event_intervals(self, events):
        action_intervals = {"start": [], "end": [], "color": []}
        for action_key in events:
            for action in events[action_key]:
                action_intervals["start"].append(action.start)
                action_intervals["end"].append(action.end)
                color = self.__map_colors(action.get_name())
                action_intervals["color"].append(color)
        return action_intervals

    def __map_colors(self, name):
        if name.startswith("SSL"):
            return self.cp[0]
        elif name.startswith("ESL"):
            return self.cp[1]
        elif name == "CD":
            return self.cp[2]
        elif name == "ES":
            return self.cp[3]
        elif name == "CR":
            return self.cp[4]
        elif name == "CF":
            return self.cp[5]
        elif name == "PD":
            return self.cp[6]
