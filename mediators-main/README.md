# Mediator

The Mediator project is aimed at improving safety and comfort when driving in a semi-autonomous vehicle by assisting and informing the driver in various ways. This repository contains a simulator for simulating such a vehicle and its driver, decision logic to decide what actions the Mediator system should take, and a framework to easily setup reinforcement learning as an alternative decision-making policy. This Readme elaborates on the different modules and how and with which options to run them. Deliverable 3.2 provides more background information regarding MEDIATOR and its components.

## Installation

To run the simulator, first clone this repository. Then run `pip install -r requirements.txt` from the root of the project to install all necessary packages. After this, the simulator can be run.

## Running the code

### Simulator

To run the simulator with the decision logic defined in decision trees, `main.py` needs to be run. This runs the simulator with the settings defined there. Options are:
- `config_file` (Required): defines the name of the YAML file that defines configurations used for running the simulator. It looks for the file in `gym_simulator/config/config_files/`. See `config.yaml` for all available config settings.
- `view_file` (Required): defines the name of the YAML file that is used for settings option concerning the rendering of the simulation. It looks for the file in `gym_simulator/config/view/`. See `view.yaml` for all available view settings.
- `driver_profile` (Required): defines the name of the YAML file specifying the (simulation of) driver preferences. It looks for the file in `mediator_system/preferences/driver_profiles`. See `driver_preferences.yaml` for all available settings.
- `tree_files` (Required): defines a non-empty list of `.tree` files on which Mediator bases its actions. It looks for the files in `mediator_system/decision_rules/decision_trees`. If multiple trees are defined, the simulator is run for every tree.
- `runs` (Required): defines how many runs the simulator will do. Each run contains random elements that are generated with a random number generator that is initialized with a seed that is specified in the config file. If more than one run is done, for each consecutive run the seed is incremented by 1. 
- `render` (Required): boolean that specifies whether to render the simulation (meaning it shows different plots of the run, based on the view settings) or not.
- `dir_name` (Required): specifies the preamble of the name of the directory in which results are stored. See [Results](#results).
- `no_threads` (Optional, default = 1): specifies the number of threads on which to run the simulation. 
- `noise` (Optional, default = None): specifies lists of noise parameters for `ttaf`, `ttau`, `ttdf`, and `ttdu`.
- `tta_levels` (Optional, default = "levels"): specifies whether to use realistic (= "levels"), optimistic (= "optimistic_levels") or pessimistic (= "pessimistic_levels") automation levels.
- `road_file` (Optional, default = None): if specified, this allows for using a predefined road for the simulation. It looks for this road in `gym_simulator/config/predefined_road`. `example_road.yaml` contains explanation on how to create a custom road. If this is not specified, the road is randomly generated.
- `include_road_data` (Optional, default = False): if true, specific road data from a route driven in Sweden is used and parsed into the simulator (containing speed and TTAF/U data). This only works if the specified `road_file` is `sweden_route/new_route.yaml`.
- `route_data_file` (Optional, default = None): if specified, this points to a file containing the data described in the previous bullet.
- `log_mediator` (Optional, default = None): setting to log some information from the decision logic. Can be "ALL" (logging at every timestep) or "ACTIONS" (logging only timesteps at which Mediator takes an action that is not Do Nothing).
- `save_fig` (Optional, default = None): if specified, saves the figure of the simulation with the specified filename. The figure is saved in `images/<TIMESTAMP>/`. For this, `render` needs to be set to true.

Instead of defining the settings directly in `main.py`, another option is to defined them in a directory in `run_configurations/`, and put all related config files in that same directory. The advantage of doing this is that simulations can easily be rerun with the same settings. `main_rc.py` contains an example of doing this. 

### Reinforcement learning

The repository also contains a framework for setting up reinforcement learning. Models can be trained and tested in this framework. 

#### Training

`train.py` can be used to train a RL model. Two example trainers are implemented to merely show how to use the framework (their performance is not necessarily expected to be good). To make your own RL algorithm, a new trainer can be implemented in `reinforcement_learning/train/`, which should inherit from `AbstractTrainer` in `abstract_trainer.py`. The trainer has the following settings:
- `config_file` (Required): same as in [Simulator](#simulator).
- `view_file` (Required): same as in [Simulator](#simulator).
- `driver_profile` (Required): same as in [Simulator](#simulator).
- `rl_settings_files` (Required): defines the name of the YAML file that specifies settings for the reinforcement learning. It looks for the file in `reinforcement_learning/settings/`.
- `save_as` (Required): defines the name of the directory in which the trained model is saved. The path is `RL_models/<METHOD_NAME>/<save_as>/`. 
- `n_processes` (Required): number of parallel processes on which to train.
- `timesteps` (Required): number of timesteps on which to train.
- `road_file` (Optional): same as in [Simulator](#simulator).

One of the implemented trainers uses an expert dataset as the basis for training. `expert_dataset.py` shows an example of how to create such an expert dataset, which bases its expertise on a decision tree.

#### Using the trained model

Once a model has been trained, it can be used for decision making. `main_rl.py` shows how to run the simulator with a trained RL model as decision maker (instead of decision trees). It takes the following settings:
- `config_file` (Required): same as in [Simulator](#simulator).
- `view_file` (Required): same as in [Simulator](#simulator).
- `driver_profile` (Required): same as in [Simulator](#simulator).
- `runs` (Required): same as in [Simulator](#simulator).
- `render` (Required): same as in [Simulator](#simulator). 
- `dir_name` (Required): same as in [Simulator](#simulator).
- `rl_settings_file` (Required): same as in [Training](#training). The settings also need to be the same as the settings used in training.
- `rl_method` (Required): the stable_baselines method used for training the model.
- `rl_model` (Required):  the name of the directory in which the model is saved.
- `road_file` (Optional): same as in [Simulator](#simulator).
- `log_mediator` (Optional): same as in [Simulator](#simulator).
- `save_fig` (Optional): same as in [Simulator](#simulator).

## Results

After every set of runs results detailing statistics and events of the runs are stored. Summarizing statistics regarding driving time, time driven in different levels, action frequency, and miscellaneous, unsafe and uncomfortable events are stored. The miscellaneous, unsafe, and uncomfortable events that are recorded are defined in `gym_simulator/evaluation/<event_type>/`, where `<event_type>` can be either "misc", "critical", or "uncomfortable". Furthermore, similar information is stored for each individual run.

The results are stored in `results/config_<dir_name>_<CONFIG_HASH>/<METHOD_NAME>/<TIMESTAMP>/`, with:
- `<dir_name>` is defined in the run settings (see [Simulator](#simulator)).
- `<CONFIG_HASH>` is a hash of the config file, ensuring that each unique config file gets its own directory. The config file is stored in `results/config_<dir_name>_<CONFIG_HASH>/`.
- `<METHOD_NAME>` is either the name of the tree (e.g., "mediator_tree" if `mediator.tree` is used) or the name of the RL method used (e.g., "RL_DQN_\<model_name\>" if DQN is used; `<model_name>` is defined in the run settings).
- `<TIMESTAMP>` defines the time at which the run is executed.

In the final directory the results are stored in a csv file together with the driver preferences and a copy of the decision tree (in case a tree is used for decision making).


## Modules
The codebase consists of different modules. This section briefly described the functions of the different modules.

### controller
This module runs the simulation by controlling the other modules. Based on the settings, it decides which decision-making system to use (RL or tree), it handles threading, and it controls the viewer (which renders the simulation).

### gym_simulator
This module contains everything relating to simulating a (semi-)autonomous car and its driver driving on various roads with possible road events, and the possible actions that can be taken by MEDIATOR. The simulation environment inherits from the OpenAI Gym interface, making it easy to apply reinforcement learning to the simulation. 

The module also contains a directory called `mediator`, which is used to communicate with the decision-making system. Different classes exist for using either a tree-based decision-making system or a RL-based decision-making system. 

### mediator_system
This module contains all the code and files that comprise the actual mediating system. It contains decision trees, a parser for these trees, driver preferences, and an interface which can be used to communicate with the system. 

A tree file can be structured as follows:
```
<condition> \\ can return a boolean, string, or int
	<possible answer to condition>:<condition> or <action> or <tree file>
		...
	<possible answer to condition>:<condition> or <action> or <tree file>
		...
	...
```
Each `<condition>` is an expression that can use any variable that is defined in the `state` variable of `get_action` in `mediator_interface.py`. In this case, the tree evaluates the expression, goes into the branch that matches the answer to the expression, and the evaluates what is after the `:`.

Each `<action>` is a String that should be one of the allowed actions defined in the config file. In this case, the tree reached a leaf and returns the action. An action can also specify additional arguments, with the syntax `<action> => <variable_name>=<value>`, where `<variable_name>` can be any string and `<value>` needs to be an expression with the same rules as for a condition.

Each `<tree file>` should be the name of a tree file that is defined somewhere in (a subdirectory of) `mediator_system/decision_rules/decision_trees`. In this case, the evaluation continues into the specified tree file. This allows for a modular design of trees.

### reinforcement_learning

This module contains everything regarding Reinforcement Learning, which includes:
- RL settings in a YAML file and a corresponding parser.
- Two implementations of RL trainers which serve as an example on how to implement this.
- Example code on how to create an expert dataset (based on a decision tree) that can be used for training.
- A loader for loading saved RL models such that they can be used for decision making.

### run_configurations

This module contains code for run configurations, meaning all settings of a run can be stored in a directory here. This can be useful when you want to be able to recreate a run at a later stage; this way, the settings can be easily stored. Currently, the module contains two directories which serve as examples. See `main_rc.py` and `main_rl.py` on how to run these.

### view

This module contains all code regarding the rendering of the simulation. There are many different plots that can be rendered, each plot has its own class. Some plots contain interactive legends, which means lines can be turned on or off by clicking on the corresponding legend item. 

### route_parser

This module contains 2 csv files containing a tabular representation of the route driven in Sweden and data from a single driver, respectively, together with parsers for parsing these files. The results of the parsing (a YAML file and a Pickle file, respectively), are already in the repository (`gym_simulator/config/predefined_road/sweden_route`) so this only needs to be used when there is new data. 