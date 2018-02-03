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
        self.is_valid_model = False
        self.syntax_errors = []
        self.semantic_errors = [] 

    def parse_model(self, model_source):
        # Reset errors
        self.syntax_errors = []
        self.semantic_errors = []

        # Try to parse
        try:
            log.debug("Parsing model source: " + model_source)
            self.model_source = model_source
            model = self.configuration.get_mm_by_ext(self.dsl_extension)\
                                      .model_from_str(model_source)
            self.last_valid_model = model
            self.is_valid_model = True
            return model
        except TextXSyntaxError as e:
            log.debug("Parsing model syntax error: " + str(e))
            self.syntax_errors.append(e)
            self.is_valid_model = False
        except TextXSemanticError as e:
            log.debug("Parsing model semantic error: " + str(e))
            self.semantic_errors.append(e)
            self.is_valid_model = False

    def fake_parse_model(self, fake_model_source):
        """
        If model is valid, we add some fake chars to it
        so we can get syntax/semantic errors from arpeggio
        and add them to the completion list.

        Returns:
            List of syntax errors
            List of semantic errors
        """
        syn_errs = []
        sem_errs = []

        try:
            log.debug("FAKE parsing model source: " + fake_model_source)
            self.configuration.get_mm_by_ext(self.dsl_extension)\
                              .model_from_str(fake_model_source)
        except TextXSyntaxError as e:
            log.debug("FAKE parsing model syntax error: " + str(e))
            syn_errs.append(e)
        except TextXSemanticError as e:
            log.debug("FAKE parsing model semantic error: " + str(e))
            sem_errs.append(e)

        return syn_errs, sem_errs

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
