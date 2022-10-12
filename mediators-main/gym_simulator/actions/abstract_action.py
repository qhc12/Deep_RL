from abc import ABC, abstractmethod


class AbstractAction(ABC):
    """
    Abstract action. Each action should inherit from this class and implement the abstract methods.
    Each action has a latest_start (defined by decision logic, for Window of Opportunity), the actual start position
    (which should be between the position at which the action is initiated and the latest start position), an earliest
    start position (which is the position at which the action was initiated, used for visualization), an end
    position, the total time it was active, and the number of steps that is was active.
    """
    def __init__(self, config, rng, start, latest_start=None):
        self.config = config
        self.rng = rng
        self.time_passed = 0.0
        self.steps_taken = 0
        self.earliest_start = start
        self.latest_start = start if latest_start is None else latest_start
        self.start = self.rng.uniform(start, self.latest_start) if \
            self.latest_start > start and self.config.random_start_in_woo else start
        self.end = self.start

    def update_latest_start(self, position, latest):
        """
        Updates the latest start position. Can be used in case the environment changes, in which case the latest start
        position may need be to shifted. If the action has already started, it is not updated.
        """
        if self.start > position:
            self.latest_start = latest if latest else position
            if self.start > self.latest_start:
                self.start = self.rng.uniform(position, self.latest_start)

    @abstractmethod
    def is_pending(self):
        """
        Returns True if the current action is not resolved yet.
        """
        pass

    @abstractmethod
    def is_successful(self):
        """
        Returns True if the action is successfully resolved. Success is defined differently for different actions.
        """
        pass

    def step(self, position):
        """
        Simple step to set the end to the position the car is currently in and to increase the time passed. Also returns
        a boolean: if False, the child class should not take a step. This has a practical reason: it prevents any
        action to terminate in the same step it was initiated, therefore having the same start and end. This way it
        would not show up the in visualization. It also prevents the action from becoming active before its actual
        start position (since that can lie after the moment the action has been initiated).

        Finally, if instant actions is set to true, the action is immediately terminated.
        """
        if position < self.start:
            return False
        self.end = position
        if self.config.instant_actions:
            self.end_action()
            self.end += 0.05
            return False
        if self.end == self.start:
            return False
        self.time_passed = self.time_passed + self.config.timestep
        self.steps_taken = self.steps_taken + 1
        return True

    @abstractmethod
    def end_action(self):
        """
        Directly sets an action to be successful or not. Used for instant action, to bypass the step method.
        """
        pass

    @abstractmethod
    def resolve(self):
        """
        This method is called when the action is not pending anymore. Depending on the action and whether it was
        successful, it may change variables.
        """
        pass

    @abstractmethod
    def get_name(self):
        """
        Get the string abbreviation of the action.
        """
        pass
