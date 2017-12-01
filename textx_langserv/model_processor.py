import itertools
import os

from textx_langserv import config, _utils

from textx.metamodel import metamodel_from_file
from textx.exceptions import TextXSemanticError, TextXSyntaxError


class ModelProcessor(object):
    """
    Used for parsing model and storing informations about parsing results
    and errors.

    Attributes:
        metamodel(TextXMetaModel): User created metamodel.
        tx_metamodel(TextXMetaModel): TextX metamodel.
        _metamodel_mtime(): Last modification of grammar file in seconds
        last_valid_model(Root rule instance): Last model that is parsed without errors
        is_valid_model(bool): Flag if last parsing was successful
        syntax_errors(list): List of TextXSyntaxErrors
        semantic_errors(list): List of TextXSemanticErrors
    """
    def __init__(self):
        try:
            self.metamodel = metamodel_from_file(config.GRAMMAR_PATH, debug=config.DEBUG)
            self._metamodel_mtime = os.path.getmtime(config.GRAMMAR_PATH)
            self.tx_metamodel = metamodel_from_file(config.TEXTX_GRAMMAR_PATH, debug=config.DEBUG)
        except OSError as e:
            pass

        self.last_valid_model = None
        self.model_source = None
        self.is_valid_model = False
        self.syntax_errors = []
        self.semantic_errors = []


    def parse_model(self, model_source):
        try:
            self._metamodel_change_check()
            
            self.metamodel = metamodel_from_file(config.GRAMMAR_PATH, debug=config.DEBUG)
            self.model_source = model_source
            model = self.metamodel.model_from_str(model_source)
            self._reset_to_valid_model(model) 

            return model
        except TextXSyntaxError as e:
            self.syntax_errors = []
            self.semantic_errors = []
            self.syntax_errors.append(e)
            self.is_valid_model = False
        except TextXSemanticError as e:
            self.syntax_errors = []            
            self.semantic_errors = []
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
            self._metamodel_change_check()
            
            self.metamodel = metamodel_from_file(config.GRAMMAR_PATH, debug=config.DEBUG)
            self.metamodel.model_from_str(fake_model_source)
        except TextXSyntaxError as e:
            syn_errs.append(e)
        except TextXSemanticError as e:
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

    
    def _reset_to_valid_model(self, model):
        self.last_valid_model = model
        self.is_valid_model = True
        self.syntax_errors = []
        self.semantic_errors = []


    def _metamodel_change_check(self):
        """
        Checking for metamodel changes.
        Consider using 'watchdog' library.
        """
        try:
            new_mtime = os.path.getmtime(config.GRAMMAR_PATH)
            if new_mtime != self._metamodel_mtime:
                self._metamodel_mtime = new_mtime
                self.metamodel = metamodel_from_file(config.GRAMMAR_PATH, debug=config.DEBUG)
        except OSError as e:
            pass

# Single instance
MODEL_PROCESSOR = ModelProcessor()