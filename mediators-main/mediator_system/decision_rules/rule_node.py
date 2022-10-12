import sys
from keyword import iskeyword

from mediator_system.decision_rules.tree_exceptions import VariableError, NoSpacesError


class RuleNode:
    """
    A RuleNode specifies a rule in the binary decision tree. It has 2 child nodes: one is visited when the rule in this
    node is true, the other when the rule in this node is false.
    """

    def __init__(self, expression):
        """
        The expression contains the rule for this node which evaluates to True or False depending on the current state.
        All variable names in the expression are replaced by 'state[<variable_name>]' such that the variable is
        read from the state variable.
        Python's eval function is used to evaluate the expression; it is stored as a lambda which can be called in the
        constructor for speedup purposes. This way, the expression gets compiled when the node gets created and doesn't
        need to be recompiled every time evaluate gets called.
        """
        self.expr = expression
        terms = [("state['{0}']".format(term) if term.isidentifier() and not iskeyword(term) else term)
                 for term in self.expr.split()]
        self.eval_string = " ".join(terms)
        self.eval_expr_func = eval('lambda state: ' + self.eval_string)
        self.children = {}

    def add_child(self, result, node):
        """
        Adds a child. The first child that is added is always the child that corresponds to the rule being true, the
        second corresponding to the rule being false.
        """
        self.children[result] = node

    def evaluate(self, state):
        """
        Evaluates the current state with the current rule. Depending on the outcome the next node in the binary
        decision tree is visited, until a leaf node (i.e. an action node) is reached.
        """
        try:
            return self.children[str(self.eval_expr_func(state))].evaluate(state)
        except KeyError as e:
            err = "The parsed tree contains an error. {0} is not a valid variable value for {1}.".\
                format(e, self.eval_string)
            raise VariableError(err) from None
        except NameError:
            err = "The parsed tree contains an error. All terms in a statement should \nhave spaces between them, " \
                  "which is possibly missing in the following statement: {0}".format(self.expr)
            raise NoSpacesError(err) from None

    def get_evaluation_path(self, state):
        result = str(self.eval_expr_func(state))
        return "{0} ==> {1}:{2}".format(self.expr, result, self.children[result].get_evaluation_path(state))

    def get_subtree_string(self, tab_level=0):
        """
        Returns a string of the tree starting from the current node.
        """
        tabs = "\t" * (tab_level + 1)
        tree_string = "{0}\n".format(self.expr)
        for res, child in self.children.items():
            tree_string = tree_string + "{0}{1}:{2}".format(tabs, res, child.get_subtree_string(tab_level + 1))
        return tree_string

    def __str__(self):
        return self.expr

    def __repr__(self):
        return str(self)
