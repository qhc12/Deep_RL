import os

from globals import ROOT_DIR


def add_path(settings, directory):
    """
    Add correct path to all the input files that are used for the runs.
    """
    settings["use_run_configurations"] = True
    path_keys = ["config_file", "view_file", "driver_profile", "road_file", "route_data_file", "rl_settings_file"]
    cwd = os.path.join(ROOT_DIR, "run_configurations", directory)
    for key, value in settings.items():
        if key in path_keys:
            settings[key] = os.path.join(cwd, value)
    return settings
