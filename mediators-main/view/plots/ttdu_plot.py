from view.plots.abstract_plot import AbstractPlot


class TTDUPlot(AbstractPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)
        self.ttdu_line = None

    @staticmethod
    def grid_height():
        return 2

    def get_grid_height(self):
        return TTDUPlot.grid_height()

    def init_plot(self, ax):
        # ax.set_ylim(-100, 2500)
        ax.set_ylim(-1, 50)
        ax.set_ylabel('Time (s)', rotation='horizontal', ha='right', va='center')
        self.ttdu_line, = ax.plot([], [], label="TTDU")
        ax.legend()

    def update_plot(self):
        self.ttdu_line.set_ydata(self.data.ttdu)
        self.ttdu_line.set_xdata(self.data.positions)
