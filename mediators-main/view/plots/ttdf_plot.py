from view.plots.abstract_plot import AbstractPlot


class TTDFPlot(AbstractPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)
        self.ttdf_line = None

    @staticmethod
    def grid_height():
        return 2

    def get_grid_height(self):
        return TTDFPlot.grid_height()

    def init_plot(self, ax):
        ax.set_ylim(-1, 30)
        ax.set_ylabel('Time (s)', rotation='horizontal', ha='right', va='center')
        self.ttdf_line, = ax.plot([], [], label='TTDF')
        ax.legend()

    def update_plot(self):
        self.ttdf_line.set_ydata(self.data.ttdf)
        self.ttdf_line.set_xdata(self.data.positions)
