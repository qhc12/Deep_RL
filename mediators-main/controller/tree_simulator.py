from controller.simulator import Simulator
from gym_simulator.envs import MediatorEnv
from gym_simulator.io.writer import Writer
from gym_simulator.mediator.tree_mediator import TreeMediator


class TreeSimulator(Simulator):

    def __init__(self, settings):
        super().__init__(settings)
        self.tree_files = settings.get("tree_files", [])
        if len(self.tree_files) == 0:
            raise ValueError("The list of tree_files needs to contain at least one existing tree.")
        self.additional_run_parameters = self.__create_trees_noise_cartesian_product()

    def __create_trees_noise_cartesian_product(self):
        """
        Creates the Cartesian product between all trees and noise parameters that are specified.
        """
        if self.noise:  # Check if all lists in the noise parameter have the same length
            it = iter(self.noise.values())
            noise_list_len = len(next(it))
            if not all(len(noise_list) == noise_list_len for noise_list in it):
                raise ValueError("Not all lists in the noise parameter are of the same length.")

            parameters = []
            for i in range(noise_list_len):
                for tree_file in self.tree_files:
                    parameters.append((tree_file, {
                        "ttaf": self.noise["ttaf"][i],
                        "ttau": self.noise["ttau"][i],
                        "ttdf": self.noise["ttdf"][i],
                        "ttdu": self.noise["ttdu"][i]
                    }))
            return parameters
        else:
            return [(tree_file, None) for tree_file in self.tree_files]

    def run(self):
        """
        Run the simulation.

        For each combination of tree and noise, a separate environment is created. Within each environment, the simulation
        is executed for as many runs as specified in the settings, and for each consecutive run the seed is incremented
        by 1.

        For instance, if runs is set to 100, 3 trees are specified, and 2 noise settings specified, then 6 (3 * 2)
        environments are created, and within each environment 100 runs are executed.
        """
        for (tree_file, noise) in self.additional_run_parameters:
            env = MediatorEnv(self.config_file, self.driver_profile, self.view_file,
                              use_run_configurations=self.use_run_configurations, road_file=self.road_file,
                              include_road_data=self.include_road_data, route_data_file=self.route_data_file,
                              render=self.render)
            self.envs.append(env)
            self.mediators.append(TreeMediator(env.config, tree_file, env.action_mapper, self.log_mediator, noise,
                                               self.tta_levels))

        self.start_simulation()

    def get_additional_run_parameters(self):
        return self.additional_run_parameters

    def write_results(self, i):
        tree = self.mediators[i].mediator_interface.tree
        Writer().write_statistics(self.config_file, self.envs[i].driver_preferences.__dict__,
                                  self.multiple_stats[i].get_dict(), tree_file=self.additional_run_parameters[i][0],
                                  parsed_tree=tree.get_subtree_string(), write_all_runs=True,
                                  config_dir_preamble=self.dir_name, noise=self.additional_run_parameters[i][1],
                                  tta_levels=self.tta_levels)
