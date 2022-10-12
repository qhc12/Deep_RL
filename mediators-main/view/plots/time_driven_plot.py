from view.plots.abstract_plot import AbstractPlot


class TimeDrivenPlot(AbstractPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)
        self.time_line = None

    @staticmethod
    def grid_height():
        return 2

    def get_grid_height(self):
        return TimeDrivenPlot.grid_height()

    def init_plot(self, ax):
        ax.set_ylim(-50, self.data.estimated_total_time + 200)
        ax.set_yticks(range(0, (int(self.data.estimated_total_time / 300) * 300) + 300, 300))
        ax.set_ylabel('Time (s)', rotation='horizontal', ha='right', va='center')
        self.time_line, = ax.plot([], [], label="Time driven")
        ax.legend()

    def update_plot(self):
        self.time_line.set_xdata(self.data.positions)
        self.time_line.set_ydata(self.data.times)
