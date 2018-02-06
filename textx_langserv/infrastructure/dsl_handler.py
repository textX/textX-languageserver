"""
Module responsible for parsing model and storing
errors and last valid model
"""
import logging
import itertools
import os

from os.path import dirname, join

from textx_langserv.utils import _utils

from textx.exceptions import TextXSemanticError, TextXSyntaxError

__author__ = "Daniel Elero"
__copyright__ = "textX-tools"
__license__ = "MIT"


log = logging.getLogger(__name__)


class TxDslHandler(object):

    def __init__(self, configuration, dsl_extension):
        self.configuration = configuration
        self.dsl_extension = dsl_extension
        self.last_valid_model = None
        self.model_source = None
        self.syntax_errors = []
        self.semantic_errors = [] 

    def parse_model(self, model_source, change_state=True):
        """
        Params:
            model_source(string): Textual file representing
                the model.
            change_state(bool): If True, object's state will
                be changed.

        Returns:
            List of syntax errors
            List of semantic errors
        """
        # Return lists
        syn_errs = []
        sem_errs = []

        # Parse
        try:
            log.debug("Parsing model source: " + model_source)
            model = self.configuration.get_mm_by_ext(self.dsl_extension)\
                                      .model_from_str(model_source)

            # Change object's state
            if change_state:
                log.debug("Parsing model. Model is valid. Source: {0}".format(
                          model_source))
                self.model_source = model_source
                self.last_valid_model = model

        except TextXSyntaxError as e:
            log.debug("Parsing model syntax error: " + str(e))
            syn_errs.append(e)
        except TextXSemanticError as e:
            log.debug("Parsing model semantic error: " + str(e))
            sem_errs.append(e)

        if change_state:
            self.syntax_errors = syn_errs
            self.semantic_errors = sem_errs

        return syn_errs, sem_errs

    @property
    def is_valid_model(self):
        return len(list(self.all_errors)) == 0

    @property
    def all_errors(self):
        return itertools.chain(self.syntax_errors, self.semantic_errors)

    @property
    def has_syntax_errors(self):
        return len(self.syntax_errors)

    @property
    def has_semantic_errors(self):
        return len(self.semantic_errors)

    def get_rule_at_position(self, position):
        """
        Returns rule at cursor position in model source file
        """
        if self.last_valid_model is None:
            return

        offset = _utils.line_col_to_pos(self.model_source, position)

        rules_dict = self.last_valid_model._pos_rule_dict

        rule = None
        for p in rules_dict.keys():
            if p[1] > offset > p[0]:
                rule = rules_dict[p]
                break

        return rule

    def get_all_rules(self):
        """
        Concatenate builtins with rule list
        """
        builtins = list(self.configuration.get_mm_by_ext(
                            self.dsl_extension).builtins.values())
        from_model = list(self.last_valid_model._pos_rule_dict.values())
        all_rules = from_model + builtins
        log.debug("Get all rules: " + ','.join(str(r) for r in all_rules))
        return all_rules
