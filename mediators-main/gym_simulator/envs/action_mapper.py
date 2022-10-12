from gym_simulator.actions.clear_request import ClearRequest
from gym_simulator.actions.correct_distraction import CorrectDistraction
from gym_simulator.actions.correct_fatigue import CorrectFatigue
from gym_simulator.actions.emergency_stop import EmergencyStop
from gym_simulator.actions.enforce_shift_level import EnforceShiftLevel
from gym_simulator.actions.prepare_driver import PrepareDriver
from gym_simulator.actions.suggest_shift_level import SuggestShiftLevel

from gym.utils import seeding


class ActionMapper:
    """
    Class that holds a record of available actions (in strings) and the corresponding int values (for the gym
    environment). Also has a function to map an int to its corresponding Action class.
    """

    def __init__(self, available_actions):
        """
        available_actions is an array containing the available actions in String format.

        The constructor creates a mapping of these string names to integers by using the index in the array.
        """
        self.rng = None
        self.available_actions = []
        inludes_cancel = "CANCEL" in available_actions
        for action in available_actions:
            self.available_actions.append(action)
            # If an action is preceded with CANCEL, cur pending action is cancelled
            if not action == "CANCEL" and inludes_cancel:
                self.available_actions.append("CANCEL" + action)
        self.actions_to_int = {}
        for i, action in enumerate(self.available_actions):
            self.actions_to_int[action] = i

    def reset_rng(self, seed):
        """
        Create a new random nummer generator.
        """
        self.rng, _ = seeding.np_random(seed)

    def get_action_string(self, i):
        """
        Returns the String representation of an action corresponding to an integer number.
        """
        return self.available_actions[i]

    def get_action_int(self, action):
        """
        Returns the Integer representation of an action corresponding to a String.
        """
        return self.actions_to_int[action]

    def map_actions(self, action_int, args, env):
        """
        action_int is an integer representing the action.
        args is a dictionary (that can be empty) that holds additional arguments for the action.
        env is the current environment.

        Returns an instance of an Action class.
        """
        action = self.get_action_string(action_int).replace('CANCEL', '')
        if action == 'DN' or action == 'CANCEL':
            return None
        if action.startswith('ESL'):
            level = min(env.config.maximum_automation_level, action[2:])
            return EnforceShiftLevel(env, self.rng, level, env.car.position, args.get('time', None),
                                     args.get('last', None))
        if action.startswith('SSL'):
            level = min(env.config.maximum_automation_level, action[2:])
            return SuggestShiftLevel(env, self.rng, level, env.car.position, args.get('time', None),
                                     args.get('last', None))
        if action == 'CF':
            return CorrectFatigue(env.config, self.rng, env.driver, env.car.position)
        if action == 'CD':
            return CorrectDistraction(env.config, self.rng, env.driver, env.car.position)
        if action == 'PD':
            return PrepareDriver(env.config, self.rng, env.driver, env.car.position)
        if action == 'CR':
            return ClearRequest(env.config, self.rng, env.driver, env.car.position)
        if action == 'ES':
            return EmergencyStop(env, self.rng)
