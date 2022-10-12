class Preferences:
    """
    Preferences class that holds preferences for the mediator system.
    """

    def __init__(self, **entries):
        self.__dict__.update(entries)
