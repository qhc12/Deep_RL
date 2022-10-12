from view.interactive_legend import InteractiveLegend
from view.plots.abstract_plot import AbstractPlot


def _map_level(level):
    if level == "L0":
        return 0
    elif level == "L2":
        return 1
    elif level == "L3":
        return 2
    elif level == "L4":
        return 3


def prettify(name):
    if name == "city":
        return "City"
    if name == "rural_minor":
        return "Rural\nminor"
    if name == "rural_major":
        return "Rural\nmajor"
    if name == "highway_link":
        return "Highway\n  link"
    if name == "highway":
        return "Highway"


class LevelsPlot(AbstractPlot):

    def __init__(self, config, data, cp):
        super().__init__(config, data, cp)
        self.max_levels_line = None
        self.opt_levels_line = None
        self.pess_levels_line = None
        self.current_level_line = None
        self.current_level_data = []
        self.last_position_index = 0
        self.legend = None

    @staticmethod
    def grid_height():
        return 2

    def get_grid_height(self):
        return LevelsPlot.grid_height()

    def init_plot(self, ax):
        x, y = self.__get_levels()
        x_opt, y_opt = self.__get_levels("optimistic_automation_levels")
        x_pess, y_pess = self.__get_levels("pessimistic_automation_levels")

        # y_axis = ["L0", "L2", "L3", "L4"]
        y_axis = [level for level in ["L0", "L2", "L3", "L4"] if level <= self.config.maximum_automation_level]
        ax.set_ylim(-0.1, len(y_axis))
        ax.set_yticks(range(len(y_axis)))
        ax.set_yticklabels(y_axis)
        self.max_levels_line, = ax.step(x, y, label="Max level")
        self.current_level_line, = ax.step([], [], label="Current level")
        if self.config.show_optimistic_lines:
            self.opt_levels_line, = ax.step(x_opt, y_opt, label="Optimistic max level")
        if self.config.show_pessimistic_lines:
            self.pess_levels_line, = ax.step(x_pess, y_pess, label="Pessimistic max level")
        ax.legend(ncol=2)
        ax.set_ylabel('Automation\nlevels', rotation='horizontal', ha='right', va='center')
        ax.set_xlabel('Distance travelled (km)')

        self.legend = InteractiveLegend(ax.get_legend())

        for merged_road_part in self.__merge_road_parts(self.data.road_parts):
            index = merged_road_part[0]
            name = merged_road_part[1]
            start = merged_road_part[2]
            end = merged_road_part[3]
            ax.axvspan(start, end, facecolor=self.cp[index], alpha=0.2)
            self.__set_text(ax, name, start, end, len(y_axis) - 0.7)

    def __set_text(self, ax, name, start, end, height):
        start_position = self.config.start_position
        end_position = self.config.end_position
        if not self.config.partial_render or start >= start_position and end <= end_position:
            ax.text(((start + end) / float(2)) - 0.1, height, name)
        elif start_position <= start <= end_position:
            ax.text(((start + end_position) / float(2)) - 0.1, height, name)
        elif start_position <= end <= end_position:
            ax.text(((start_position + end) / float(2)) - 0.1, height, name)

    def update_plot(self):
        x, y = self.__get_levels()
        self.max_levels_line.set_ydata(y)
        self.max_levels_line.set_xdata(x)

        if self.opt_levels_line:
            x_opt, y_opt = self.__get_levels("optimistic_automation_levels")
            self.opt_levels_line.set_ydata(y_opt)
            self.opt_levels_line.set_xdata(x_opt)

        if self.pess_levels_line:
            x_pess, y_pess = self.__get_levels("pessimistic_automation_levels")
            self.pess_levels_line.set_ydata(y_pess)
            self.pess_levels_line.set_xdata(x_pess)

        for i in range(self.last_position_index, len(self.data.positions)):
            self.current_level_data.append(_map_level(self.data.current_levels[i]))
        self.last_position_index = len(self.data.positions)

        self.current_level_line.set_ydata(self.current_level_data)
        self.current_level_line.set_xdata(self.data.positions)

    def __get_levels(self, level_type="max_automation_levels"):
        max_levels = getattr(self.data, level_type)
        x = [0.0]
        y = [_map_level(max_levels[0][0])]
        for level in max_levels:
            x.append(level[1])
            y.append(_map_level(level[0]))
        return x, y

    def __merge_road_parts(self, road_parts):
        """
        Make tuples of index, name, start, end
        """
        road_types = list(self.config.allowed_road_types.keys())
        merged_road_parts = []
        for road_part in road_parts:
            name = road_part.road_type
            index = road_types.index(name)
            if len(merged_road_parts) > 0 and merged_road_parts[-1][0] == index:
                merged_road_parts[-1][3] = road_part.end
            else:
                merged_road_parts.append([index, prettify(name), road_part.start, road_part.end])
        return merged_road_parts
