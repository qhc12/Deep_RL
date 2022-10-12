import gym
from gym import spaces

from gym_simulator.car.car_class import Car
from gym_simulator.config.config_parser import ConfigParser
from gym_simulator.config.road_parser import RoadParser
from gym_simulator.driver.driver_class import Driver
from gym_simulator.envs.action_mapper import ActionMapper
from gym_simulator.envs.observations.observation_manager import ObservationManager
from gym_simulator.envs.reward.reward_factory import RewardFactory
from gym_simulator.evaluation.evaluation import EvaluationMetrics
from gym_simulator.evaluation.safety_events import SafetyEvents
from gym_simulator.roads.road import Road
from gym_simulator.data.data import Data
from mediator_system.preferences.preferences_parser import PreferencesParser
from reinforcement_learning.rl_settings_parser import RLSettingsParser


class MediatorEnv(gym.Env):
    """
    Environment for simulating MEDIATOR.
    """

    metadata = {"render.modes": ["human"]}

    def __init__(self, config_file, driver_preferences_file, view_file, use_run_configurations=False, road_file=None,
                 include_road_data=False, route_data_file=None, render=True, rl_settings_file=None):
        """
        Initializes everything related to the environment.
        """
        # Holds all settings for the simulation
        self.config = ConfigParser(config_file, view_file, use_run_configurations).parse()
        self.driver_preferences = PreferencesParser(driver_preferences_file, use_run_configurations).parse()
        # Update the config with the driver preferences
        self.config.__dict__.update(**self.driver_preferences.__dict__)
        # Hold the settings that are specifially aimed at RL
        self.rl_settings = RLSettingsParser(rl_settings_file, use_run_configurations).parse() \
            if rl_settings_file else None
        # Parse the preset road if it's included
        self.preset_road = RoadParser(road_file, include_road_data, route_data_file, use_run_configurations).parse(
            self.config) if road_file is not None else None
        self.action_mapper = ActionMapper(self.config.available_actions)  # Used for initializing actions
        self.allow_render = render  # If True, plots visualizing the simulation will be rendered

        self.road = None  # Road object
        self.car = None  # Car object
        self.driver = None  # Driver object
        self.safety = None  # Safety object
        self.comfort = None  # Comfort object
        self.evaluation = None  # Evaluation object

        self.pending_action = None  # List with pending actions
        self.last_action = None  # Last action taken
        self.action_args = {}  # Dictionary with (possible) arguments for an action
        self.action_ended = None  # True if action ended in the current timestep
        self.resolved_action = None  # The action that was resolved in this timestep
        self.future_action = None  # A future action
        self.future_args = None  # The args for the future action

        self.data = None  # Keeps track of history of values for rendering

        # Other variables
        self.steps = None  # Incremented every time step function is called
        self.time_passed = None  # Incremented at every time step to keep track of total simulated time
        self.switched = None  # True if automation level switched in this timestep

        self.current_seed = None  # The seed used for the simulation
        self.done = False  # When True, the current simulation terminates

        # Action space used for gym environment
        # self.action_space = spaces.Discrete(len(self.action_mapper.available_actions), self.current_seed)
        self.action_space = spaces.Discrete(len(self.action_mapper.available_actions))
        # If rl_settings are set, initialize RL classes
        if self.rl_settings:
            self.observation_manager = ObservationManager(self.rl_settings)  # Handles observations
            self.observation_space = self.observation_manager.get_observation_space()  # Observation space
            # Used to calculate rewards based on current state
            self.reward_calculator = RewardFactory(self.rl_settings).get_reward_calculator(self)

        self.cur_worker = None  # The thread that the environment is running in, which emits a signal to the viewer

    def step(self, gym_action):
        """
        Function that defines one timestep in the simulation. In that timestep:
            - A possible new incoming action is added to the pending actions.
            - All pending actions take a step (most take more than one step to terminate) and are updated (some may be
                resolved)
            - The car takes a step (moving forward on the road)
            - The driver takes a step (possibly getting tired or distracted)
            - The road takes a step (updating road values s.a. current road part)
            - Any Evaluations events take a step (regarding safety, comfort, etc.)
            - Data is updated (storing all relevant data from the simulation, used for visualization)
        Each of the above entities have their own class, more details about their respective step functions can be found
        in these classes.
        """
        self.last_action = None
        self.switched = False
        self.action_ended = False
        self.resolved_action = None
        self.steps += 1

        # If action is preceded by CANCEL, it means pending action should be cancelled
        action_string = self.action_mapper.get_action_string(gym_action)
        if action_string.startswith('CANCEL'):
            self.pending_action = None

        # If an action is not to Do Nothing (DN) or to CANCEL, add the new action to the list of pending actions
        if 'DN' not in action_string and not action_string == 'CANCEL' and self.pending_action is None:
            self.last_action = self.action_mapper.map_actions(gym_action, self.action_args, self)
            self.pending_action = self.last_action
        # Step through the action
        if self.pending_action:
            self.pending_action.step(self.car.position)
            if not self.pending_action.is_pending():
                self.pending_action.resolve()
                self.action_ended = True
                self.resolved_action = self.pending_action

        self.pending_action = self.pending_action if self.pending_action and self.pending_action.is_pending() else None
        # Update all entities in simulation
        self._update()
        self.future_action = None

        # Simulation terminates when either done is set to True (e.g. by ES) or the car has finished driving the road
        self.done = self.done or self.car.position >= self.road.total_distance
        if self.done:
            self.evaluation.finalize(self.data, self.time_passed)

        self.action_args = {}
        if self.rl_settings:
            return self.get_observations(), self.reward_calculator.get_reward(), self.done, {}
        else:
            return {}, None, self.done, {}

    def _update(self):
        if self.preset_road is not None and self.preset_road.includes_route_data() and \
                self.steps >= len(self.preset_road.route_data['timestamps']):
            self.done = True

        self.car.step(self.time_passed)
        self.driver.step()
        self.road.step(self.car)
        self.safety.step(self.last_action, self.resolved_action, self.time_passed, self.switched)
        self.evaluation.step(self.last_action is not None, self.pending_action is not None, self.action_ended,
                             self.car.current_level, self.time_passed)
        self.data.update(self)
        self.future_action = None

        if self.preset_road is not None and self.preset_road.includes_route_data() and not self.done:
            self.time_passed = self.preset_road.route_data['timestamps'][self.steps]
        else:
            self.time_passed += self.config.timestep

    def get_observations(self):
        return self.observation_manager.get_observations(self)

    def obs_arr_to_dict(self, obs_arr):
        return self.observation_manager.obs_space_class.reverse_transform(obs_arr)

    def reset(self):
        """
        Creates all the objects for the simulation.
        """
        if self.current_seed is None:
            self.current_seed = self.config.seed
        else:
            self.current_seed = self.current_seed + 1

        self.road = Road(self.config, self.current_seed + 1, self.preset_road)
        self.car = Car(self.config, self.current_seed + 2, self.road)
        self.driver = Driver(self.config, self.current_seed + 3, self.car, self.road.estimated_total_time)
        self.safety = SafetyEvents(self.config, self.driver, self.car)
        self.evaluation = EvaluationMetrics(self.config, self.safety)

        self.pending_action = None
        self.action_mapper.reset_rng(self.current_seed + 4)
        self.action_ended = False

        # Other variables
        self.steps = 0
        self.time_passed = 0.0
        self.switched = False

        self.data = Data(self)
        self.done = False
        return self.get_observations() if self.rl_settings else {}

    def render(self, mode="human"):
        """
        Possibly renders the simulation.

        Returns True if it is being rendered, else False.
        """
        if self.allow_render and ((self.config.render_intermediate and self.car.position >= self.config.start_from and
                                   self.time_passed % self.config.render_interval == 0) or self.done):
            self.cur_worker.sig_render.emit()
            return True
        return False
