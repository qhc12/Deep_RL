import inspect
import os

from gym_simulator.evaluation.safety_factory import create_safety_event
from gym_simulator.evaluation.safety_types import SafetyType as st

import importlib


class SafetyEvents:
    """
    Class to hold and manage all safety events.
    """

    def __init__(self, config, driver, car):
        self.config = config
        self.driver = driver
        self.car = car
        self.current_step_is_active = {}
        self.active_steps = {}
        for safety_type in st:
            self.current_step_is_active[safety_type] = False
            self.active_steps[safety_type] = 0

        self.time_passed = 0
        self.time_of_last_switch = None

        # Build a directory mapping all class names to their uninitialized objects. Used to automatically initialize
        # correct event.
        evaluation_classes = {}
        base_dir = os.path.join('gym_simulator', 'evaluation')
        for child_dir in next(os.walk(base_dir))[1]:
            if not child_dir == "__pycache__":
                full_dir = os.path.join(base_dir, child_dir)
                files = os.listdir(full_dir)
                for file in files:
                    if not file == "__pycache__":
                        module = 'gym_simulator.evaluation.{0}.{1}'.format(child_dir, file[:-3])
                        for name, cls in inspect.getmembers(importlib.import_module(module), inspect.isclass):
                            if cls.__module__ == module:
                                evaluation_classes[name] = cls

        # Array holding possible safety events
        self.possible_events = []
        for metric in self.config.evaluation_metrics:
            self.possible_events.append(evaluation_classes[metric])
        self.possible_events.reverse()
        self.active_events = []
        self.all_events = []

    def step(self, last_action, resolved_action, time_passed, has_switched):
        """
        Step through all active safety events.

        last_action is an object holding the last action that was taken (or None if no action was taken yet).
        resolved_action is an action that is resolved in the current timestep.
        time_passed is the time passed in seconds in the simulation so far.
        has_switched is a boolean indicating whether levels have been switched in the current timestep.

        These variables are needed for some of the safety events.
        """
        self.time_passed = time_passed

        for event in self.active_events:
            event.step()

        self.active_events = [event for event in self.active_events if event.is_pending]

        for event in self.possible_events:
            if any(isinstance(ev, event) for ev in self.active_events):
                continue

            # Each event is created, and when it is active it is added to the active_events, else it is discarded
            evt = create_safety_event(event, self, last_action, resolved_action)
            if evt.is_active():
                self.active_events.append(evt)
                self.all_events.append(evt)

        # Stores some info for results
        for safety_type in st:
            self.current_step_is_active[safety_type] = self._safety_type_is_active(safety_type)
            if self.current_step_is_active[safety_type]:
                self.active_steps[safety_type] += 1

        if has_switched:
            self.time_of_last_switch = self.time_passed

    def _safety_type_is_active(self, safety_type):
        """
        Returns true if there is a safety event with the specified type active currently.
        """
        return any(ev.type == safety_type for ev in self.active_events)

    def safety_event_is_active(self, name):
        """
        Returns true if the safety event is active currently.
        """
        return any(ev.name == name for ev in self.active_events)
