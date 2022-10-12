import os

from globals import ROOT_DIR


class Loader:
    """
    Class to Load saved RL models.
    """

    def __init__(self, method, model_name, env):
        self.method = method
        self.model_name = model_name
        self.env = env

    def load(self):
        return self.method.load(os.path.join(ROOT_DIR, "RL_models", self.method.__name__, self.model_name,
                                             "trained_model"), self.env)
