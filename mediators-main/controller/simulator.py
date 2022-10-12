import sys
from abc import ABC, abstractmethod

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSlot

from gym_simulator.evaluation.statistics import Statistics

from controller.runner import MultithreadedRunner, RenderRunner

import time

from pathos.multiprocessing import ProcessingPool as Pool


class Simulator(ABC):
    """
    Abstract class to run the simulator for one or more runs using PyQT5 and a fork of Python's multiprocessing module.
    """

    def __init__(self, settings):
        """
        Initialize all simulation settings.
        """
        self.use_run_configurations = settings.get("use_run_configurations", False)
        self.config_file = settings.config_file
        self.view_file = settings.view_file
        self.road_file = settings.get("road_file", None)
        self.include_road_data = settings.get("include_road_data", False)
        self.route_data_file = settings.get("route_data_file", None)
        self.noise = settings.get("noise", None)
        self.tta_levels = settings.get("tta_levels", "levels")
        self.runs = settings.runs
        self.render = settings.render
        self.dir_name = settings.dir_name
        self.no_threads = min(settings.get("no_threads", 1), self.runs)
        self.driver_profile = settings.driver_profile
        self.log_mediator = settings.get("log_mediator", None)
        self.save_fig = settings.get("save_fig", None)
        self.additional_run_parameters = None
        self.threads = []
        self.envs = []  # This will hold the environment object
        self.mediators = []  # This will hold the mediator object
        self.multiple_stats = []  # This will hold the stats over all the runs
        self.start_time = None  # This will be initialized at start of the simulation
        self.finished_count = 0

    @abstractmethod
    def run(self):
        """
        Run the simulation.
        """
        pass

    @abstractmethod
    def get_additional_run_parameters(self):
        """
        Returns the different noise settings and (in the case of the tree_simulator) trees for which the simulation
        needs to be run.
        """
        pass

    def start_simulation(self):
        """
        Starts the simulation. In case of multithreading, starts all threads.
        """
        self.start_time = time.time()

        if self.render or self.no_threads == 1:
            # Initiate a PyQt5 application
            self.qapp = QApplication(sys.argv)

            for i in range(len(self.get_additional_run_parameters())):
                # Initiate the thread in which this run will be executed
                thread = QThread()
                thread.setObjectName('Environment')

                # Create a Statistics object to hold stats
                self.multiple_stats.append(Statistics(self.envs[i].config))

                # Initiate the worker that will execute the run
                worker = RenderRunner(i, self.envs[i], self.mediators[i], self.multiple_stats[i], self.runs,
                                      self.render, self.save_fig)

                worker.moveToThread(thread)  # Move it into the created thread so it runs in there
                worker.sig_done.connect(lambda index: self.__finalize(index))  # Finalize the thread

                # Store thread and worker to list to prevent garbage collection
                self.threads.append((thread, worker))
                # Connect the running of the simulation to the start of the thread
                thread.started.connect(worker.run_simulation)
                thread.start()  # Start the thread so the simulation run will start

            # Execute the PyQt5 application, causing it to run
            self.qapp.exec()
        else:
            for i in range(len(self.get_additional_run_parameters())):
                # Get a list of tuples defining seed starts and number of runs for all processes
                seed_starts_and_runs = self.__calculate_seed_starts_and_runs()
                # Initiate a worker object
                worker = MultithreadedRunner()
                # Workaround to pass a function with multiple arguments to the map function of Pool
                run_sim = lambda x: worker.run_simulation(*x)

                args = []  # List that contains tuples, where each tuples contains arguments for one process
                for thread_no in range(self.no_threads):
                    seed_start, total_runs = seed_starts_and_runs[thread_no]
                    args.append((self.envs[i], self.mediators[i], thread_no, total_runs, seed_start))

                # Initiate a ParallelProcessing Pool
                pool = Pool(nodes=self.no_threads)
                # Run the function
                results = pool.map(run_sim, args)
                # Since the processes have no shared memory, stats need to be merged here
                stats = results[0]
                for j in range(1, len(results)):
                    stats.merge(results[j])
                self.multiple_stats.append(stats)
                self.__finalize(i)

    def __calculate_seed_starts_and_runs(self):
        """
        Function that calculates a list of tuples containing a seed start and number of runs in the case of
        parallel processing.
        """
        # If there are fewer runs than threads, each run simply gets its own thread
        if self.runs <= self.no_threads:
            return [(i, 1) for i in range(self.runs)]

        # This calculates the minimum number of runs for each thread (since int rounds down)
        min_runs = int(self.runs / self.no_threads)
        # If there is a remainder, it means the first <remainder> processes perform one extra run
        remainder = self.runs % self.no_threads
        seeds_and_runs = []
        cur_seed = 0
        for i in range(self.no_threads):
            total_runs = min_runs + 1 if i < remainder else min_runs
            seeds_and_runs.append((cur_seed, total_runs))
            cur_seed += total_runs
        return seeds_and_runs

    @pyqtSlot()
    def __finalize(self, i):
        """
        Writes stats to a file and exits the application if no GUI is open.
        """
        self.multiple_stats[i].finalize(time.time() - self.start_time)
        self.write_results(i)
        self.finished_count += 1

        if not self.render and self.finished_count == len(self.get_additional_run_parameters()):
            # When not rendering, immediately quit the application once a run is done. Else, the app will quit
            # when closing the window(s).
            sys.exit()

    @abstractmethod
    def write_results(self, i):
        """
        Write the results to a file.
        """
        pass
