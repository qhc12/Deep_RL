from abc import ABC, abstractmethod


class AbstractNode(ABC):
    """
    AbstractNode class from which other node classes should inherit, to ensure they implement the abstract methods
    in this class.
    """

    @abstractmethod
    def evaluate(self, state):
        """
        Evaluate the current state.
        """
        pass

    @abstractmethod
    def get_evaluation_path(self, state):
        """
        Returns a string of the path through the tree given the current state.
        """
        pass

    @abstractmethod
    def get_subtree_string(self, tab_level=0):
        """
        Get a string representation of the subtree starting at this node.
        """
        pass

    def __repr__(self):
        return str(self)
