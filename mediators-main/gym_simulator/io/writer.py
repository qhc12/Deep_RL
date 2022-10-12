import csv
import datetime
import hashlib
import os
import yaml
from shutil import copyfile


class Writer:
    """
    Class to write statistics from multiple runs to file.
    """

    def hash_config(self, config_file):
        """
        Calculates the md5 hash for the config file
        """
        hash_md5 = hashlib.md5()
        with open(config_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def write_statistics(self, config_file, settings, stats, tree_file=None, parsed_tree="", method=None, model_name="",
                         write_all_runs=False, config_dir_preamble="", noise=None, tta_levels="levels"):
        """
        Writes the statistics to file. The location of the results is
        'results/config_[config_dir_preamble]_[config_hash]/[tree_file_name]_tree/[current_date]/'
        In this folder the decision tree with which the simulation was run is stored along with a results.csv file
        detailing the results.
        The config file which is used for the simulation is stored in the parent config directory, since all runs
        in that directory are run with the same config file, so it only needs to be stored once.

        Parameters:
            config_file: the config file that was used for the run(s)
            settings: the driver preferences used
            stats: a dictionary containing all stats for all the runs
            tree_file: the name of the tree file used (default is None, in case of RL)
            parsed_tree: a string with the parsed tree (default is "", in case of RL)
            method: the RL method used in case of RL (default is None, in case of tree)
            model_name: the name of the RL model (default is "", in case of tree)
            write_all_runs: boolean indicating whether statistics for each individual run should also be written
            config_dir_preamble: the preamble that is placed in the name of directory where the config file is stored
            noise: the noise parameters used for this run (default is None in case no noise is used)
            tta_levels: in case pessimistic or optimistic levels are used, this is reflected in the directory name.
        """
        config_loc = os.path.join("gym_simulator", "config", "config_files", config_file)
        config_hash = self.hash_config(config_loc)

        # a directory with the hash of this config does not yet exist
        config_hash_dir = os.path.join("results", "config_{0}_{1}".format(config_dir_preamble, config_hash))
        if not os.path.isdir(config_hash_dir):
            os.makedirs(config_hash_dir)
            copyfile(config_loc, os.path.join(config_hash_dir, "config.yaml"))

        decision_maker_dir = "{0}_tree".format(tree_file[:-5]) if tree_file else "RL_{0}_{1}".format(method.__name__,
                                                                                                     model_name)
        if noise:
            decision_maker_dir = "{0}_noise_ttaf_{1}_ttau_{2}_ttdf_{3}_ttdu_{4}".format(decision_maker_dir,
                                                                                        noise["ttaf"], noise["ttau"],
                                                                                        noise["ttdf"], noise["ttdu"])
        if not tta_levels == "levels":
            decision_maker_dir = "{0}_{1}".format(decision_maker_dir, tta_levels)
        directory = os.path.join(config_hash_dir, decision_maker_dir,
                                 datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

        os.makedirs(directory)
        with open(os.path.join(directory, "preferences.yaml"), 'w', newline='', encoding='utf-8') as f:
            yaml.dump(settings, f, default_flow_style=False, sort_keys=False)
        if tree_file:
            with open(os.path.join(directory, tree_file), 'w', newline='', encoding='utf-8') as f:
                f.write(parsed_tree)

        runs = stats.pop("runs", None)
        with open(os.path.join(directory, "results.csv"), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(stats.keys())
            w.writerow(stats.values())
            w.writerow(["Runs"])
            w.writerow(runs[0].keys())
            for run in runs:
                if write_all_runs or (run['Number of unsafe events'] > 0 or run['Number of uncomfortable events'] > 0):
                    w.writerow(run.values())
