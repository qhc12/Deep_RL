from view.plots.abstract_plot import AbstractPlot


class SpeedPlot(AbstractPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)
        self.speed_line = None

    @staticmethod
    def grid_height():
        return 2

    def get_grid_height(self):
        return SpeedPlot.grid_height()

    def init_plot(self, ax):
        ax.set_ylim(-2, 122)
        ax.set_ylabel('Speed (km/h)', rotation='horizontal', ha='right', va='center')
        self.speed_line, = ax.plot([], [], label="Speed")
        ax.legend()

    def update_plot(self):
        self.speed_line.set_xdata(self.data.positions)
        self.speed_line.set_ydata(self.data.speeds)
