from textx.metamodel import metamodel_from_file
from textx.exceptions import TextXSemanticError, TextXSyntaxError

import config
import _utils
import itertools


class ModelProcessor(object):
    """
    Used for parsing model and storing informations about parsing results
    and errors.

    Attributes:
        metamodel(TextXMetaModel): User created metamodel.
        tx_metamodel(TextXMetaModel): TextX metamodel.
        last_valid_model(Root rule instance): Last model that is parsed without errors
        is_valid_model(bool): Flag if last parsing was successful
        syntax_errors(list): List of TextXSyntaxErrors
        semantic_errors(list): List of TextXSemanticErrors
    """
    def __init__(self):
        self.metamodel = metamodel_from_file(config.GRAMMAR_PATH, debug=config.DEBUG)
        self.tx_metamodel = metamodel_from_file(config.TEXTX_GRAMMAR_PATH, debug=config.DEBUG)
        self.last_valid_model = None
        self.model_source = None
        self.is_valid_model = False
        self.syntax_errors = []
        self.semantic_errors = []


    def parse_model(self, model_source):
        try:
            self.metamodel = metamodel_from_file(config.GRAMMAR_PATH, debug=config.DEBUG)
            self.model_source = model_source
            model = self.metamodel.model_from_str(model_source)
            self._reset_to_valid_model(model) 

            return model
        except TextXSyntaxError as e:
            self.syntax_errors = []
            self.syntax_errors.append(e)
            self.is_valid_model = False
        except TextXSemanticError as e:
            self.semantic_errors = []
            self.semantic_errors.append(e)
            self.is_valid_model = False


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
        offset = _utils.line_col_to_pos(self.model_source, position)

        rules_dict = self.last_valid_model._pos_rule_dict

        rule = None
        for p in rules_dict.keys():
            if offset > p[0] and offset < p[1]:
                rule = rules_dict[p]
                break

        return rule

    
    def _reset_to_valid_model(self, model):
        self.last_valid_model = model
        self.is_valid_model = True
        self.syntax_errors = []
        self.semantic_errors = []


# Single instance
MODEL_PROCESSOR = ModelProcessor()