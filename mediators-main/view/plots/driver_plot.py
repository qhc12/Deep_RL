from gym_simulator.config.allowed_values import DriverEvent
from view.plots.abstract_plot import AbstractPlot

import seaborn as sns


def _map_driver_request(request):
    if request is None:
        return 0
    elif request == "L0":
        return 1
    elif request == "L2":
        return 2
    elif request == "L3":
        return 3
    elif request == "L4":
        return 4


class DriverPlot(AbstractPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)
        self.lines = {}
        self.legend = None

    @staticmethod
    def grid_height():
        return 2

    def get_grid_height(self):
        return DriverPlot.grid_height()

    def init_plot(self, ax):
        allowed_driver_events = self.config.allowed_driver_events
        ax.set_ylim(-0.5, 4.5)
        ax.set_yticks(range(5))
        label = ""
        cmap = sns.color_palette()
        if DriverEvent.FATIGUE in allowed_driver_events:
            self.lines['fatigue'], = ax.step([], [], label="Fatigue", color=cmap[0])
            label = label + "Fatigue/"
        if DriverEvent.DISTRACTION in allowed_driver_events:
            self.lines['distraction'], = ax.step([], [], label="Distraction", color=cmap[1])
            label = label + "Distraction/"
        if DriverEvent.NDRT in allowed_driver_events:
            self.lines['ndrt'], = ax.step([], [], color=cmap[2])
            # label = label + "NDRT/"
        label = label[:-1] + "\nlevel"
        ax.set_ylabel(label, rotation='horizontal', ha='right', va='center')

        if DriverEvent.DRIVER_REQUEST in allowed_driver_events:
            self.lines['request'], = ax.step([], [], label="Driver Request", color=cmap[3])
            ax2 = ax.twinx()
            y_axis = ["None", "L0", "L2", "L3", "L4"]
            ax2.set_ylim(-0.5, 4.5)
            ax2.set_yticks(range(5))
            ax2.set_yticklabels(y_axis)
            ax2.grid(None)
            ax2.set_ylabel('Driver request', rotation='horizontal', ha='left', va='center')
        ax.legend()

    def update_plot(self):
        positions = self.data.positions
        for key, line in self.lines.items():
            line.set_xdata(positions)
            if key == 'fatigue':
                line.set_ydata(self.data.fatigue)
            elif key == 'distraction':
                line.set_ydata(self.data.distraction)
            elif key == 'ndrt':
                line.set_ydata(self.data.ndrt)
            elif key == 'request':
                line.set_ydata([_map_driver_request(request) for request in self.data.driver_request])
