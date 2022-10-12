from keyword import iskeyword

from mediator_system.decision_rules.node import AbstractNode
from mediator_system.decision_rules.tree_exceptions import NoSpacesError


class ActionNode(AbstractNode):
    """
    An ActionNode defines a leaf node in the tree and specifies which action should be taken when evaluation reaches
    this leaf.
    """

    def __init__(self, action, args):
        self.action = action
        self.parameters = {}
        if args:
            args = args.split(",")
            for arg in args:
                name, value = arg.strip().split("=")
                value_string = " ".join([("state['{0}']".format(term) if term.isidentifier() and not iskeyword(term)
                                         else term) for term in value.split()])
                value_func = eval('lambda state: ' + value_string)
                self.parameters[name] = value_func

    def evaluate(self, state):
        args = {}
        for key in self.parameters.keys():
            try:
                args[key] = self.parameters[key](state)
            except NameError:
                err = "The parsed tree contains an error. All terms in a statement should \nhave spaces between them, "\
                      "which is possibly missing in the following statement: {0}".format(self.parameters[key])
                raise NoSpacesError(err) from None

        return self.action, args

    def get_evaluation_path(self, state):
        return self.action

    def get_subtree_string(self, tab_level=0):
        return self.action + "\n"

    def __str__(self):
        return "{0}".format(self.action)
