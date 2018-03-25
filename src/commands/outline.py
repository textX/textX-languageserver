"""
This module is responsible for creating and returning
outline tree data.
"""
import os
from os.path import join, dirname

from ..utils._utils import pos_to_line_col
from ..utils.uris import to_abs_path
from json import JSONEncoder

__author__ = "Nemanja Starčev"
__copyright__ = "textX-tools"
__license__ = "MIT"


class MyEncoder(JSONEncoder):

    def default(self, o):
        return o.__dict__


class Node(object):
    def __init__(self, type, label, icon,
                 start, end, start_line,
                 start_point_in_line, end_line, end_point_in_line):
        self.type = type
        self.label = label
        self.icon = icon
        self.start = start
        self.end = end
        self.start_line = start_line
        self.start_point_in_line = start_point_in_line
        self.end_line = end_line
        self.end_point_in_line = end_point_in_line
        self.children = []


class OutlineTree(object):
    def __init__(self, model_source, outline_model, current_model):
        self.model_source = model_source
        self.outline_model = outline_model
        self.outline_path = dirname(outline_model._tx_filename)
        self.nodes = []
        self.start_position_in_lines = []
        self.visit_rule(current_model)

    def visit_rule(self, rule, mult='1'):
        if (mult == '1'):
            subrules = rule._tx_attrs
            values = {}
            for subrule in subrules:
                child = getattr(rule, subrule)
                attr = subrules[subrule]
                if attr.cont is False:
                    if attr.mult == '1':
                        values[subrule] = child.name
                        continue
                    else:
                        for item in child:
                            self.proccess_rule(values, rule, item.name)
                        continue
                if child is None:
                    continue
                if attr.ref is False:
                    values[subrule] = child
                    continue
                self.visit_rule(child, attr.mult)
            self.proccess_rule(values, rule)
        else:
            for item in rule:
                self.visit_rule(item)

    def proccess_rule(self, values, rule, label=None):
        rule_name = type(rule).__name__
        if len(values) == 0 and label is None:
            return
        for outline_rule in self.outline_model.rules:
            if outline_rule.name == rule_name:
                if label is None:
                    label = self.get_label(values, outline_rule.label.names)
                icon = None
                if outline_rule.icon is not None:
                    icon = to_abs_path(self.outline_path,
                                       outline_rule.icon.path)
                start_line, start_point_in_line = pos_to_line_col(
                                                    self.model_source,
                                                    rule._tx_position)
                end_line, end_point_in_line = pos_to_line_col(
                                                    self.model_source,
                                                    rule._tx_position_end)
                node = Node(rule_name, label, icon,
                            rule._tx_position, rule._tx_position_end,
                            start_line, start_point_in_line,
                            end_line, end_point_in_line)
                self.nodes.append(node)

    def get_label(self, values, names):
        label = ""
        for name in names:
            for key, value in values.items():
                if name.id == key:
                    label += value
                    break
                if name.string != '':
                    label += name.string
                    break
        return label

    def make_tree(self):
        children = self.determine_parent_child_relation()
        for node in self.nodes:
            if node in self.nodes:
                self.remove_grandchildren(node)
        for child in children:
            if child in self.nodes:
                self.nodes.remove(child)
        return MyEncoder().encode(self.nodes)

    def determine_parent_child_relation(self):
        children = []
        for parent in self.nodes:
            for child in self.nodes:
                if self.is_parent_child_relation_valid(parent, child):
                    children.append(child)
                    parent.children.append(child)
        return children

    def is_parent_child_relation_valid(self, parent, child):
        if parent.start < child.start and parent.end > child.end:
            return True
        return False

    def remove_grandchildren(self, node):
        children = []
        for child in node.children:
            for grandchild in child.children:
                if grandchild not in children:
                    children.append(grandchild)
        for child in children:
            if child in self.nodes:
                node.children.remove(child)
