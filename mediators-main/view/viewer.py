from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QPushButton, QScrollArea, QHBoxLayout, QVBoxLayout, QWidget, QMainWindow, QApplication

import matplotlib as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import seaborn as sns

from view.util import map_view

# This plot backend is needed for the GUI
plt.use('Qt5Agg')


class Viewer(QMainWindow):
    """
    Viewer class that is used to plot view of the simulation.
    """

    def __init__(self, config, count):
        super().__init__()

        self.config = config
        self.cond = None  # A wait condition from the worker, which can be woken up from the viewer
        self.worker = None  # Will contain the worker that does all the work
        self.initiated = False  # True when all plots have been initiated
        self.data = None  # Will contain the data for the GUI

        # A list which contains all subplots
        self.plots = [map_view(view) for view in self.config.views if map_view(view) is not None]
        # The total number of rows in the grid, based on the plots that are included
        self.grid_height = sum(plot.grid_height() for plot in self.plots)

        self.cp = sns.color_palette("pastel")
        sns.set_theme()
        sns.set_context("paper")

        self.setWindowTitle("Figure " + str(count))
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        layout = QVBoxLayout(self.widget)
        self.widget.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.layout().setSpacing(0)

        button_layout = QHBoxLayout()
        self.buttonResume = QPushButton('Resume', self)
        self.buttonPause = QPushButton('Pause', self)
        self.buttonResume.clicked.connect(self.__resume)
        self.buttonPause.clicked.connect(self.__pause)
        button_layout.addWidget(self.buttonResume)
        button_layout.addWidget(self.buttonPause)
        button_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(button_layout)

        fig_width = max((2.5 / 3.0) * config.road_length, 15)  # Width of figure in inches
        fig_height = max(self.grid_height / 1.8, 5)  # Height of figure in inches
        self.fig = Figure(figsize=(fig_width, fig_height), tight_layout={"pad": 2, "w_pad": 2, "h_pad": 0.2})
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        layout.addWidget(NavigationToolbar(self.canvas, self))

        # If the plots do not have to fit the screen, create a scrollarea so scrollbars appear on the plots if their
        # size exceeds the screen size
        if not config.fit_screen:
            scroll = QScrollArea(self.widget)
            scroll.setAlignment(Qt.AlignCenter)
            scroll.setWidget(self.canvas)
            layout.addWidget(scroll)

    def __pause(self):
        self.worker.pause()

    def __resume(self):
        self.worker.resume()

    def __init_plots(self):
        """
        Function to initialize the plots, after which the GUI will be shown.
        """
        self.initiated = True
        self.data = self.worker.env.data

        # Create all plots that are specified in the view.yaml file
        for i, plot in enumerate(self.plots):
            self.plots[i] = plot(self.config, self.data, self.cp)

        # Create the accompanying axes and set their limits
        axes = self.__get_axes()
        self.__set_x_limits(axes)
        self.__set_x_labels(axes)
        ax_iterator = iter(axes)

        # Initialize the plots with their respective axes
        for plot in self.plots:
            plot.init_plot(next(ax_iterator))

        # Show the GUI
        self.show()
        self.activateWindow()
        self.raise_()
        self.showMaximized()

    def __get_axes(self):
        axes = []

        # Used to specify the relative heights of the subplots
        gs = gridspec.GridSpec(self.grid_height, 1)
        cur_height = 0
        for plot in self.plots:
            size = plot.get_grid_height()
            axes.append(self.fig.add_subplot(gs[cur_height:cur_height + size, :]))
            cur_height = cur_height + size

        return axes

    def __set_x_limits(self, axes):
        # Sets the limits of the x-axis for all subplots, since this is the same for all subplots
        for ax in axes:
            ax.set_xticks(range(int(self.data.road_length) + 1))
            if self.config.partial_render:
                ax.set_xlim(self.config.start_position, self.config.end_position)
            else:
                ax.set_xlim(-0.01 * self.data.road_length, self.data.road_length + 0.01 * self.data.road_length)

    def __set_x_labels(self, axes):
        # Only the top plot has a label on the x-axis on top, the others do not (for space saving purposes)
        for i, ax in enumerate(axes):
            if i == 0:
                ax.xaxis.set_label_position('top')
                ax.xaxis.tick_top()
            else:
                ax.set_xticklabels([])

    @pyqtSlot()
    def update_plots(self):
        """
        Updates the data in the plots with the latest data available from the simulation. This way, the simulation
        can be plotted live.
        """
        if not self.initiated:
            self.__init_plots()

        for plot in self.plots:
            plot.update_plot()

        self.fig.canvas.draw()
        # Process events so rendering is paused as soon as pause button is clicked
        QApplication.instance().processEvents()
        # The runner is paused while the viewer renders, this wakes the runner back up to continue
        self.cond.wakeAll()
