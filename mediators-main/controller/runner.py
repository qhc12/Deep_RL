import datetime
import os

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QMutex, QWaitCondition
from PyQt5.QtWidgets import QApplication

from gym_simulator.evaluation.statistics import Statistics
from view.viewer import Viewer


class SingleRun(QtCore.QObject):
    """
    Class that is used to execute a single run in an environment.
    """
    sig_render = QtCore.pyqtSignal()  # Signal sent to viewer to trigger a rerender

    def __init__(self, env, mediator, stats, seed_start, viewer=None, save_fig=None, start_time=None):
        super().__init__()
        self.env = env
        self.mediator = mediator
        self.stats = stats
        self.seed_start = seed_start

        # Mutex and WaitCondition are used together to pause the worker until it is woken up again.
        # This is useful when rendering the simulator.
        self.mtx = QMutex()
        self.cond = QWaitCondition()
        self.paused = False

        self.viewer = viewer
        self.save_fig = save_fig
        self.start_time = start_time
        if self.viewer is not None:
            self.viewer.worker = self
            self.viewer.cond = self.cond
            self.sig_render.connect(self.viewer.update_plots)

    def run(self):
        # If the current_seed is None it means it is the first run. It is initialized to the seed it should start at
        # minus one, because reset is called right after, which increments the seed by 1.
        if self.env.current_seed is None:
            self.env.current_seed = self.env.config.seed + self.seed_start - 1
        self.env.reset()  # Environment is always reset at beginning of run

        # Set the worker of the environment to this class, such that the env can emit the render signal
        self.env.cur_worker = self
        print('Seed: {0}'.format(self.env.current_seed))

        self.__render()
        done = False
        cum_reward = 0
        reward_initialized = False
        while not done:
            if self.viewer is not None:
                # Process events here to ensure it pauses immediately
                QApplication.instance().processEvents()
            # Possibly pause the simulation here
            self.mtx.lock()
            if self.paused:
                self.cond.wait(self.mtx)
            self.mtx.unlock()

            if self.mediator.is_random():
                action = self.env.action_space.sample()
            else:
                action = self.mediator.get_action(self.env)  # Get the action from the mediator
                if self.env.allow_render and "FUTURE_ACTIONS" in self.env.config.views:
                    # Set a future action for the mediator
                    self.mediator.set_future_action(self.env)
            obs, reward, done, info = self.env.step(action)  # Take a step in the environment with the action
            if reward:
                reward_initialized = True
                cum_reward += reward
            self.__render()

        if reward_initialized:
            print("Total reward: {0}".format(cum_reward))
        self.__save_figure()
        self.stats.update(self.env)  # When the run is finished, update the stats

    def __render(self):
        # If rendered is True, it means the environment emitted a render signal at this step
        rendered = self.env.render()
        if rendered:
            # When the environment rendered, it means the viewer needs time to update. So the worker is paused until
            # the viewer updated its plots, after which it will wake the worker up.
            self.mtx.lock()
            self.cond.wait(self.mtx)
            self.mtx.unlock()

    def __save_figure(self):
        if self.viewer is not None and self.save_fig is not None:
            directory = os.path.join("images", self.start_time)
            if not os.path.isdir(directory):
                os.makedirs(directory)
            file_name = self.env.current_seed
            if self.mediator.noise:
                noise = self.mediator.noise
                file_name = "{0}_noise_ttaf_{1}_ttau_{2}_ttdf_{3}_ttdu_{4}".format(file_name, noise["ttaf"],
                                                                                   noise["ttau"], noise["ttdf"],
                                                                                   noise["ttdu"])
            file_name = "{0}_{1}".format(file_name, self.save_fig)
            self.viewer.fig.savefig(os.path.join(directory, file_name), dpi=600)

    def pause(self):
        """
        Pause the current run.
        """
        self.mtx.lock()
        self.paused = True
        self.mtx.unlock()

    def resume(self):
        """
        Resume the current run if it was paused.
        """
        self.mtx.lock()
        self.paused = False
        self.mtx.unlock()
        self.cond.wakeAll()


class MultithreadedRunner:
    """
    Class that runs a simulation. This can be part of a larger pool.
    """

    def run_simulation(self, env, mediator, worker_id, runs, seed_start):
        """
        Run the simulation until it's done.
        """
        print('Process {0} started from seed {1} to {2}'.format(worker_id, env.config.seed + seed_start,
                                                                env.config.seed + seed_start + runs - 1))
        stats = Statistics(env.config)

        for i in range(runs):
            run = SingleRun(env, mediator, stats, seed_start)
            run.run()

        print('Process {0} is finished'.format(worker_id))
        return stats


class RenderRunner(QtCore.QObject):
    """
    Class that runs a simulation on one thread, and possibly renders it.
    """

    sig_done = QtCore.pyqtSignal(int)  # Signal send to simulator to indicate the run is finished

    def __init__(self, worker_id, env, mediator, stats, runs, render, save_fig):
        super().__init__()
        self.worker_id = worker_id
        self.env = env
        self.mediator = mediator
        self.stats = stats
        self.runs = runs
        self.render = render
        self.save_fig = save_fig

        self.viewers = []
        if self.render:
            for i in range(runs):
                self.viewers.append(Viewer(self.env.config, i))

    @pyqtSlot()
    def run_simulation(self):
        """
        Run the simulation until it's done.
        """
        start_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        for i in range(self.runs):
            run = SingleRun(self.env, self.mediator, self.stats, i,
                            self.viewers[i] if len(self.viewers) > 0 else None, self.save_fig, start_time)
            run.run()

        self.sig_done.emit(self.worker_id)  # Tell the simulator that this run is finished
