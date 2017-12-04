import itertools
import os

from os.path import dirname, join

from utils import _utils

from textx.metamodel import metamodel_from_file
from textx.exceptions import TextXSemanticError, TextXSyntaxError

this_folder = dirname(__file__)

class TxDslHandler(object):
   
    def __init__(self):
        self.metamodel = None
        self.last_valid_model = None
        self.model_source = None
        self.is_valid_model = False
        self.syntax_errors = []
        self.semantic_errors = []
    

    def set_metamodel(self, metamodel):
        self.metamodel = metamodel
        self._reset_to_valid_model(None)


    def parse_model(self, model_source):
        try:
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
            gram = 'C:\\Users\\Daniel\\Desktop\\TEXTX-LANGUAGESERVER\\textx-languageserver\\examples\\SimpleLang\\eg1_grammar.tx'
            new_mtime = os.path.getmtime(gram)
            if new_mtime != self._metamodel_mtime:
                self._metamodel_mtime = new_mtime
                self.metamodel = metamodel_from_file(gram, debug=False)
        except OSError as e:
            pass
