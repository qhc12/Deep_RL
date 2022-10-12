from abc import ABC, abstractmethod


class AbstractPlot(ABC):

    def __init__(self, config, data, cp):
        self.config = config
        self.data = data
        self.cp = cp

    @staticmethod
    @abstractmethod
    def grid_height():
        pass

    @abstractmethod
    def get_grid_height(self):
        pass

    @abstractmethod
    def init_plot(self, ax):
        pass

    @abstractmethod
    def update_plot(self):
        pass
