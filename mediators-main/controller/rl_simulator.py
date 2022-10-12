from controller.simulator import Simulator
from gym_simulator.envs import MediatorEnv
from gym_simulator.io.writer import Writer
from gym_simulator.mediator.rl_mediator import RLMediator
from reinforcement_learning.load import Loader


class RLSimulator(Simulator):

    def __init__(self, settings, sub_proc_vec_env):
        super().__init__(settings)
        self.rl_settings_file = settings.get("rl_settings_file", None)
        self.rl_model = settings.get("rl_model", None)
        self.rl_method = settings.get("rl_method", None)
        self.sub_proc_vec_env = sub_proc_vec_env
        self.additional_run_parameters = self.__build_noise_dicts()

    def __build_noise_dicts(self):
        """
        Create a list with different noise settings, if these are specified in the settings.
        """
        if self.noise:
            it = iter(self.noise.values())
            noise_list_len = len(next(it))
            if not all(len(noise_list) == noise_list_len for noise_list in it):
                raise ValueError("Not all lists in the noise parameter are of the same length.")

            parameters = []
            for i in range(noise_list_len):
                parameters.append({
                    "ttaf": self.noise["ttaf"][i],
                    "ttau": self.noise["ttau"][i],
                    "ttdf": self.noise["ttdf"][i],
                    "ttdu": self.noise["ttdu"][i]
                })

            return parameters
        else:
            return [None]

    def run(self):
        """
        Run the simulation.

        For each noise setting, a separate environment is created. Within each environment, the simulation
        is executed for as many runs as specified in the settings, and for each consecutive run the seed is incremented
        by 1.
        """
        for noise in self.additional_run_parameters:
            env = MediatorEnv(self.config_file, self.driver_profile, self.view_file,
                              use_run_configurations=self.use_run_configurations, road_file=self.road_file,
                              include_road_data=self.include_road_data, route_data_file=self.route_data_file,
                              render=self.render, rl_settings_file=self.rl_settings_file)
            vec_env = self.sub_proc_vec_env([lambda: env])
            self.envs.append(env)
            self.mediators.append(RLMediator(Loader(self.rl_method, self.rl_model, vec_env).load(), self.log_mediator,
                                             noise, self.tta_levels))

        self.start_simulation()

    def get_additional_run_parameters(self):
        return self.additional_run_parameters

    def write_results(self, i):
        Writer().write_statistics(self.config_file, self.envs[i].driver_preferences.__dict__,
                                  self.multiple_stats[i].get_dict(), method=self.rl_method, model_name=self.rl_model,
                                  write_all_runs=True, config_dir_preamble=self.dir_name,
                                  noise=self.additional_run_parameters[i], tta_levels=self.tta_levels)
