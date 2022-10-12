from gym.utils import seeding

from gym_simulator.config.allowed_values import DriverEvent
from gym_simulator.events.driver_events.distraction import Distraction
from gym_simulator.events.driver_events.driver_event_generator import DriverEventGenerator
from gym_simulator.events.driver_events.ndrt import NDRT


class Driver:
    """
    Class to hold driver information, s.a. fatigue level, distraction level, and TTDU and TTDF based on this level.
    """

    def __init__(self, config, seed, car, estimated_total_time):
        """
        Inits the driver class.

        car is an instance of the car class such that the driver knows in which car he's driving.
        estimated_total_time is an estimation of the total time the drive will take, which is used for probability
            calculation of possible driver events.
        """
        self.config = config
        self.rng, _ = seeding.np_random(seed)
        self.car = car
        self.timestep = config.timestep
        self.fatigue = config.initial_fatigue
        # Set to True if CF action fails, indicating fatigue is physiological and thus not correctable
        self.uncorrectable_fatigue = None
        self.distraction = config.initial_distraction
        # Distraction level from previous timestep, used to see if distraction level decreased
        self.previous_distraction = config.initial_distraction
        self.ndrt = 0  # Type of distraction which is used when driving in L3 or L4
        self.driver_request = None
        # The driver_event_generator is used for generating driver events (fatigue, distraction, NDRT, driver request)
        self.driver_event_generator = DriverEventGenerator(self.config, self.rng, estimated_total_time)
        self.pending_events = []  # Active driver events
        self.all_events = []  # Keeps track of all events that occurred during the simulation, for visualisation
        # Keeps track for each shift level of the last time a suggestions to that level was declined
        self.last_decline = {'L0': None, 'L2': None, 'L3': None, 'L4': None}

        self.ttdu_distraction = self._distraction_ttdu()  # Calculates the TTDU based on distraction
        self.ttdu_fatigue = self._fatigue_ttdu()  # Calculates the TTDU based on fatigue
        self.ttdu_ndrt = self._ndrt_ttdu()  # Calculates the TTDU based on NDRT
        # When True, it means a fatigue event occurred and thus TTDU/F based on fatigue needs to be recalculated
        self.update_fatigue = True
        # When True, it means a distraction event occurred and thus TTDU/F based on distraction needs to be recalculated
        self.update_distraction = True
        self._update_ttdu()
        self._update_ttdf()

    def step(self):
        """
        If necessary, distractions are converted to NDRT or vice versa (when a level change occurs).

        A new driver event is possibly (with some probability) generated.

        All active driver events take a step.

        TTDU and TTDF are updated.
        """
        self.convert_distraction_to_ndrt()
        self.convert_ndrt_to_distraction()
        # Possibly generates a new driver event
        new_event = self.driver_event_generator.generate_next_event(self.car, self.pending_events)
        if new_event:
            self.all_events.append(new_event)
            self.pending_events.append(new_event)
        # Step through the pending events, and update the list afterwards (possibly some aren't pending anymore)
        for event in self.pending_events:
            event.step(self, self.car)
        self.pending_events = [event for event in self.pending_events if event.is_pending]

        # Update ttdu and ttdf
        self._update_ttdu()
        self._update_ttdf()
        # Set these to False, because unless a fatigue or distraction event happens, the TTDU can simply be
        # decremented by 1 timestep in each step
        self.update_fatigue = False
        self.update_distraction = False
        # Set the current distraction level as the previous level for the next step
        self.previous_distraction = self.distraction

    def convert_distraction_to_ndrt(self):
        """
        Function checks if there are any active distraction events, while the car is driving in an automated level
        (L3 or L4). In that case, a distraction is converted into an NDRT.
        """
        ndrt = None
        for event in self.pending_events:
            if event.get_enum() == DriverEvent.DISTRACTION and self.car.current_level > "L2":
                event.is_pending = False
                event.end = self.car.position
                ndrt = NDRT(self.config, self.rng, event.end)
                ndrt.changed = True
                self.ndrt = self.distraction
                self.distraction = 0
                self.update_distraction = True
                break
        if ndrt:
            self.pending_events.append(ndrt)
            self.all_events.append(ndrt)

    def convert_ndrt_to_distraction(self):
        """
        Function checks if there are any active NDRT events, while the car is driving in L0 or L2. In that case, an NDRT
        event is converted into a distraction.
        """
        distraction = None
        for event in self.pending_events:
            if event.get_enum() == DriverEvent.NDRT and self.car.current_level < "L3":
                event.is_pending = False
                event.end = self.car.position
                distraction = Distraction(self.config, self.rng, event.end)
                distraction.increased = True
                self.distraction = self.ndrt
                self.ndrt = 0
                self.update_distraction = True
                break
        if distraction:
            self.pending_events.append(distraction)
            self.all_events.append(distraction)

    def end_events(self, end, event_type):
        """
        End all pending driver events of the given event_type.
        """
        for event in self.pending_events:
            if event.get_enum() == event_type:
                event.is_pending = False
                event.end = end

    def _update_ttdf(self):
        """
        Updates the TTDF as the maximum TTDF based on distraction, NDRT, and fatigue
        """
        self.ttdf = max(self._distraction_ttdf(), self._fatigue_ttdf(), self._ndrt_ttdf())

    def _ndrt_ttdf(self):
        """
        Returns the TTDF value in the YAML file belonging to current NDRT level
        """
        return self.config.ttdf['ndrt'][self.ndrt]

    def _distraction_ttdf(self):
        """
        Returns the TTDF value in the YAML file belonging to current distraction level
        """
        return self.config.ttdf['distraction'][self.distraction]

    def _fatigue_ttdf(self):
        """
        Returns the TTDF value in the YAML file belonging to current fatigue level
        """
        return self.config.ttdf['fatigue'][self.fatigue]

    def _update_ttdu(self):
        """
        Updates the TTDU values for fatigue and distraction -> if an distraction or fatigue event happens, the value
        needs to be updated based on the new fatigue/distraction level. Else, the value decreases linearly.

        For NDRT, the TTDU value is a constant based on the NDRT level.

        After calculating the indiviaual TTDU levels, the minimum is taken as the actual TTDU value of the driver.
        """
        # If fatigue should be updated (due to change in fatigue level), take the predefined value in the ttd.yaml file
        # belonging to that fatigue level
        if self.update_fatigue:
            self.ttdu_fatigue = self._fatigue_ttdu()
        else:
            # If no update necessary, either decrement TTDU by one timestep, unless it's zero, then keep it at zero
            self.ttdu_fatigue = max(0, self.ttdu_fatigue - self.timestep)
            # Possibly update fatigue level based on TTDU such that ttdu_fatigue and fatigue level are always congruous
            if self.ttdu_fatigue <= self.config.ttdu['fatigue'][self.car.current_level][4]:
                self.fatigue = 4
            elif self.ttdu_fatigue <= self.config.ttdu['fatigue'][self.car.current_level][self.fatigue + 1]:
                self.fatigue = self.fatigue + 1

        # Distraction level changed and thus ttdu_distraction needs to be updated
        if self.update_distraction:
            # If distraction decreased, simply recalculate the ttdu_distraction value based on ttd.yaml
            if self.distraction < self.previous_distraction:
                self.ttdu_distraction = self._distraction_ttdu()
            # If it increased, take the minimum between the value from the ttd.yaml file and the updated value (this can
            # already be lower than the predefined value if the distraction was going on for a while)
            else:
                self.ttdu_distraction = min(self._distraction_ttdu(), max(0, self.ttdu_distraction - self.timestep))
        else:
            # No update necessary, simply decrement until 0
            self.ttdu_distraction = max(0, self.ttdu_distraction - self.timestep)

        self.ttdu_ndrt = self._ndrt_ttdu()

        # The TTDU is the minimum between TTDU for fatigue and distraction and NDRT
        self.ttdu = min(self.ttdu_fatigue, self.ttdu_distraction, self.ttdu_ndrt)
        # No updates needed unless something changes
        self.update_fatigue = False
        self.update_distraction = False

    def _distraction_ttdu(self):
        """
        Returns the TTDU value in the YAML file belonging to current distraction level
        """
        return self.config.ttdu['distraction'][self.car.current_level][self.distraction]

    def _fatigue_ttdu(self):
        """
        Returns the TTDU value in the YAML file belonging to current fatigue level
        """
        return self.config.ttdu['fatigue'][self.car.current_level][self.fatigue]

    def _ndrt_ttdu(self):
        """
        Returns the TTDU value in the YAML file belonging to current fatigue level
        """
        return self.config.ttdu['ndrt'][self.car.current_level][self.ndrt]
