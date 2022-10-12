from view.interactive_legend import InteractiveLegend
from view.plots.abstract_plot import AbstractPlot

import seaborn as sns


class TTAFPlot(AbstractPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)
        self.ttafl2_line = None
        self.parsed_ttafl2_line = None
        self.real_ttafl2_line = None
        self.optimistic_ttafl2_line = None
        self.pessimistic_ttafl2_line = None
        self.ttafl3_line = None
        self.real_ttafl3_line = None
        self.optimistic_ttafl3_line = None
        self.pessimistic_ttafl3_line = None
        self.ttafl4_line = None
        self.real_ttafl4_line = None
        self.optimistic_ttafl4_line = None
        self.pessimistic_ttafl4_line = None
        self.legend = None

    @staticmethod
    def grid_height():
        return 2

    def get_grid_height(self):
        return TTAFPlot.grid_height()

    def init_plot(self, ax):
        ax.set_ylim(-10, 450)
        ax.set_ylabel('Time (s)', rotation='horizontal', ha='right', va='center')

        cmap = sns.color_palette()
        columns = 0
        if self.config.maximum_automation_level >= "L2":
            self.ttafl2_line, = ax.plot([], [], label="TTAFL2", color=cmap[0])
            if self.config.includes_route_data:
                self.parsed_ttafl2_line, = ax.plot([], [], label="Parsed TTAF", color='red')
            if self.config.show_real_ttafu:
                self.real_ttafl2_line, = ax.plot([], [], label="RealTTAFL2", color=cmap[9])
            if self.config.show_optimistic_lines:
                self.optimistic_ttafl2_line, = ax.plot([], [], label="TTAFL2-opt", color=cmap[2])
            if self.config.show_pessimistic_lines:
                self.pessimistic_ttafl2_line, = ax.plot([], [], label="TTAFL2-pes", color=cmap[3])
            columns += 1
        if self.config.maximum_automation_level >= "L3":
            self.ttafl3_line, = ax.plot([], [], label="TTAFL3", color=cmap[1])
            if self.config.show_real_ttafu:
                self.real_ttafl3_line, = ax.plot([], [], label="RealTTAFL3", color='black')
            if self.config.show_optimistic_lines:
                self.optimistic_ttafl3_line, = ax.plot([], [], label="TTAFL3-opt", color=cmap[4])
            if self.config.show_pessimistic_lines:
                self.pessimistic_ttafl3_line, = ax.plot([], [], label="TTAFL3-pes", color=cmap[5])
            columns += 1
        if self.config.maximum_automation_level >= "L4":
            self.ttafl4_line, = ax.plot([], [], label="TTAFL4", color=cmap[6])
            if self.config.show_real_ttafu:
                self.real_ttafl4_line, = ax.plot([], [], label="RealTTAFL4", color='yellow')
            if self.config.show_optimistic_lines:
                self.optimistic_ttafl4_line, = ax.plot([], [], label="TTAFL4-opt", color=cmap[7])
            if self.config.show_pessimistic_lines:
                self.pessimistic_ttafl4_line, = ax.plot([], [], label="TTAFL4-pes", color=cmap[8])
            columns += 1

        ax.legend(ncol=columns)
        self.legend = InteractiveLegend(ax.get_legend(), ["TTAFL2-opt", "TTAFL2-pes", "RealTTAFL2",
                                                          "TTAFL3-opt", "TTAFL3-pes", "RealTTAFL3",
                                                          "TTAFL4-opt", "TTAFL4-pes", "RealTTAFL4"])

    def update_plot(self):
        positions = self.data.positions

        if self.ttafl2_line:
            self.ttafl2_line.set_ydata(self.data.ttaf["L2"])
            self.ttafl2_line.set_xdata(positions)
        if self.real_ttafl2_line:
            self.real_ttafl2_line.set_ydata(self.data.real_ttaf["L2"])
            self.real_ttafl2_line.set_xdata(positions[:len(self.data.real_ttaf["L2"])])
        if self.parsed_ttafl2_line:
            self.parsed_ttafl2_line.set_ydata(self.data.real_route_ttaf_l2)
            self.parsed_ttafl2_line.set_xdata(positions)
        if self.optimistic_ttafl2_line:
            self.optimistic_ttafl2_line.set_ydata(self.data.optimistic_ttaf["L2"])
            self.optimistic_ttafl2_line.set_xdata(positions)
        if self.pessimistic_ttafl2_line:
            self.pessimistic_ttafl2_line.set_ydata(self.data.pessimistic_ttaf["L2"])
            self.pessimistic_ttafl2_line.set_xdata(positions)
        if self.ttafl3_line:
            self.ttafl3_line.set_ydata(self.data.ttaf["L3"])
            self.ttafl3_line.set_xdata(positions)
        if self.real_ttafl3_line:
            self.real_ttafl3_line.set_ydata(self.data.real_ttaf["L3"])
            self.real_ttafl3_line.set_xdata(positions[:len(self.data.real_ttaf["L3"])])
        if self.optimistic_ttafl3_line:
            self.optimistic_ttafl3_line.set_ydata(self.data.optimistic_ttaf["L3"])
            self.optimistic_ttafl3_line.set_xdata(positions)
        if self.pessimistic_ttafl3_line:
            self.pessimistic_ttafl3_line.set_ydata(self.data.pessimistic_ttaf["L3"])
            self.pessimistic_ttafl3_line.set_xdata(positions)
        if self.ttafl4_line:
            self.ttafl4_line.set_ydata(self.data.ttaf["L4"])
            self.ttafl4_line.set_xdata(positions)
        if self.real_ttafl4_line:
            self.real_ttafl4_line.set_ydata(self.data.real_ttaf["L4"])
            self.real_ttafl4_line.set_xdata(positions[:len(self.data.real_ttaf["L4"])])
        if self.optimistic_ttafl4_line:
            self.optimistic_ttafl4_line.set_ydata(self.data.optimistic_ttaf["L4"])
            self.optimistic_ttafl4_line.set_xdata(positions)
        if self.pessimistic_ttafl4_line:
            self.pessimistic_ttafl4_line.set_ydata(self.data.pessimistic_ttaf["L4"])
            self.pessimistic_ttafl4_line.set_xdata(positions)
