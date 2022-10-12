class RLSettings:
    """
    Class to hold RL Settings.
    """

    def __init__(self, **entries):
        self.__dict__.update(entries)
