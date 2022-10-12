from view.interactive_legend import InteractiveLegend
from view.plots.abstract_plot import AbstractPlot

import seaborn as sns


class TTAUPlot(AbstractPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)
        self.ttaul2_line = None
        self.parsed_ttaul2_line = None
        self.real_ttaul2_line = None
        self.optimistic_ttaul2_line = None
        self.pessimistic_ttaul2_line = None
        self.ttaul3_line = None
        self.real_ttaul3_line = None
        self.optimistic_ttaul3_line = None
        self.pessimistic_ttaul3_line = None
        self.ttaul4_line = None
        self.real_ttaul4_line = None
        self.optimistic_ttaul4_line = None
        self.pessimistic_ttaul4_line = None
        self.legend = None

    @staticmethod
    def grid_height():
        return 2

    def get_grid_height(self):
        return TTAUPlot.grid_height()

    def init_plot(self, ax):
        # ax.set_ylim(-10, self.data.estimated_total_time + 10)
        ax.set_ylim(-10, 800)
        ax.set_ylabel('Time (s)', rotation='horizontal', ha='right', va='center')

        cmap = sns.color_palette()
        columns = 0
        if self.config.maximum_automation_level >= "L2":
            self.ttaul2_line, = ax.plot([], [], label="TTAUL2", color=cmap[0])
            if self.config.includes_route_data:
                self.parsed_ttaul2_line, = ax.plot([], [], label="Parsed TTAU", color='red')
            if self.config.show_real_ttafu:
                self.real_ttaul2_line, = ax.plot([], [], label="RealTTAUL2", color=cmap[9])
            if self.config.show_optimistic_lines:
                self.optimistic_ttaul2_line, = ax.plot([], [], label="TTAUL2-opt", color=cmap[2])
            if self.config.show_pessimistic_lines:
                self.pessimistic_ttaul2_line, = ax.plot([], [], label="TTAUL2-pes", color=cmap[3])
            columns += 1
        if self.config.maximum_automation_level >= "L3":
            self.ttaul3_line, = ax.plot([], [], label="TTAUL3", color=cmap[1])
            if self.config.show_real_ttafu:
                self.real_ttaul3_line, = ax.plot([], [], label="RealTTAUL3", color='black')
            if self.config.show_optimistic_lines:
                self.optimistic_ttaul3_line, = ax.plot([], [], label="TTAUL3-opt", color=cmap[4])
            if self.config.show_pessimistic_lines:
                self.pessimistic_ttaul3_line, = ax.plot([], [], label="TTAUL3-pes", color=cmap[5])
            columns += 1
        if self.config.maximum_automation_level >= "L4":
            self.ttaul4_line, = ax.plot([], [], label="TTAUL4", color=cmap[6])
            if self.config.show_real_ttafu:
                self.real_ttaul4_line, = ax.plot([], [], label="RealTTAUL4", color='yellow')
            if self.config.show_optimistic_lines:
                self.optimistic_ttaul4_line, = ax.plot([], [], label="TTAUL4-opt", color=cmap[7])
            if self.config.show_pessimistic_lines:
                self.pessimistic_ttaul4_line, = ax.plot([], [], label="TTAUL4-pes", color=cmap[8])
            columns += 1
        ax.legend(ncol=columns)
        self.legend = InteractiveLegend(ax.get_legend(), ["TTAUL2-opt", "TTAUL2-pes", "RealTTAUL2",
                                                          "TTAUL3-opt", "TTAUL3-pes", "RealTTAUL3",
                                                          "TTAUL4-opt", "TTAUL4-pes", "RealTTAUL4"])

    def update_plot(self):
        positions = self.data.positions

        if self.ttaul2_line:
            self.ttaul2_line.set_ydata(self.data.ttau["L2"])
            self.ttaul2_line.set_xdata(positions)
        if self.real_ttaul2_line:
            self.real_ttaul2_line.set_ydata(self.data.real_ttau["L2"])
            self.real_ttaul2_line.set_xdata(positions[:len(self.data.real_ttau["L2"])])
        if self.parsed_ttaul2_line:
            self.parsed_ttaul2_line.set_ydata(self.data.real_route_ttau_l2)
            self.parsed_ttaul2_line.set_xdata(positions)
        if self.optimistic_ttaul2_line:
            self.optimistic_ttaul2_line.set_ydata(self.data.optimistic_ttau["L2"])
            self.optimistic_ttaul2_line.set_xdata(positions)
        if self.pessimistic_ttaul2_line:
            self.pessimistic_ttaul2_line.set_ydata(self.data.pessimistic_ttau["L2"])
            self.pessimistic_ttaul2_line.set_xdata(positions)
        if self.ttaul3_line:
            self.ttaul3_line.set_ydata(self.data.ttau["L3"])
            self.ttaul3_line.set_xdata(positions)
        if self.real_ttaul3_line:
            self.real_ttaul3_line.set_ydata(self.data.real_ttau["L3"])
            self.real_ttaul3_line.set_xdata(positions[:len(self.data.real_ttau["L3"])])
        if self.optimistic_ttaul3_line:
            self.optimistic_ttaul3_line.set_ydata(self.data.optimistic_ttau["L3"])
            self.optimistic_ttaul3_line.set_xdata(positions)
        if self.pessimistic_ttaul3_line:
            self.pessimistic_ttaul3_line.set_ydata(self.data.pessimistic_ttau["L3"])
            self.pessimistic_ttaul3_line.set_xdata(positions)
        if self.ttaul4_line:
            self.ttaul4_line.set_ydata(self.data.ttau["L4"])
            self.ttaul4_line.set_xdata(positions)
        if self.real_ttaul4_line:
            self.real_ttaul4_line.set_ydata(self.data.real_ttau["L4"])
            self.real_ttaul4_line.set_xdata(positions[:len(self.data.real_ttau["L4"])])
        if self.optimistic_ttaul4_line:
            self.optimistic_ttaul4_line.set_ydata(self.data.optimistic_ttau["L4"])
            self.optimistic_ttaul4_line.set_xdata(positions)
        if self.pessimistic_ttaul4_line:
            self.pessimistic_ttaul4_line.set_ydata(self.data.pessimistic_ttau["L4"])
            self.pessimistic_ttaul4_line.set_xdata(positions)
