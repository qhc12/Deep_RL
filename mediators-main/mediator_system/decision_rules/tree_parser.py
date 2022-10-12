import os
import pathlib

from mediator_system.decision_rules.action_node import ActionNode
from mediator_system.decision_rules.rule_node import RuleNode
from mediator_system.decision_rules.tree_exceptions import IndentError


class TreeParser:
    """
    A parser for the tree files, parsing a decision tree into rule and action nodes.
    """
    trees = []  # List of all tree files in (sub)directories of directory decision_trees
    paths = {}  # Directory that maps each tree file to its respective path

    def __init__(self, tree_name, available_actions):
        self.actions = available_actions
        # All tree files are the decision_trees directory. self.trees contains all the names of these files,
        # which can be used to parse subtrees (defined in a different file)
        if len(TreeParser.trees) == 0:
            for root, dirs, files in os.walk(pathlib.Path(__file__).parent / 'decision_trees'):
                for file in files:
                    TreeParser.trees.append(file)
                    if file in TreeParser.paths:
                        raise ValueError("There are multiple files named {0}. Each tree file should have a unique name."
                                         .format(file))
                    TreeParser.paths[file] = os.path.join(root, file)

        with open(TreeParser.paths[tree_name]) as tree_file:
            tree_lines = tree_file.readlines()
            self.tree_lines = [line.replace('\t', '    ') for line in tree_lines if line.strip().split("#", 1)[0]]

    def parse(self):
        root = None
        lines = iter(self.tree_lines)
        stack = []
        indent_levels = set()
        prev_indent = 0
        for line in lines:
            indent = len(line) - len(line.lstrip())
            indent = indent // 4

            # Check if the indentation is correct
            if (indent < prev_indent and indent not in indent_levels) or \
                    (indent > prev_indent and indent - prev_indent > 1):
                raise IndentError("Indentation is wrong at the following line: {0}".format(line))
            indent_levels.add(indent)
            prev_indent = indent

            # Parse line
            line = line.strip().split("#", 1)[0]  # Strip any comments
            result_and_expr = line.split(':')
            if len(result_and_expr) == 1:
                node = self.parse_node(line)
                root = node
            else:
                res = result_and_expr[0].strip()
                expr = result_and_expr[1].strip()
                node = self.parse_node(expr)

            stack[indent:] = [node]
            if len(stack) != 1:
                stack[-2].add_child(res, node)

        return root

    def parse_node(self, expr):
        expr_and_args = expr.split("=>")
        expr = expr_and_args[0].strip()
        args = None
        if len(expr_and_args) > 1:
            args = expr_and_args[1].strip()

        if expr in self.actions:
            return ActionNode(expr, args)
        elif expr in TreeParser.trees:
            return TreeParser(expr, self.actions).parse()
        else:
            return RuleNode(expr)
