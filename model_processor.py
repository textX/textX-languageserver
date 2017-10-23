from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export, model_export
from textx.exceptions import TextXError
from textx.metamodel import TextXMetaModel
from textx.textx import PRIMITIVE_PYTHON_TYPES
from textx.const import MULT_ONE

import config
import _utils

class Model(object):

    def __init__(self):
        self._metamodel = metamodel_from_file(config.GRAMMAR_PATH, debug=config.DEBUG)
        self._tx_metamodel = metamodel_from_file(config.TEXTX_GRAMMAR_PATH, debug=config.DEBUG)
        self._last_valid_model = None
        self._model_source = None
        self._exceptions = []

    @property
    def metamodel(self):
        return self._metamodel

    @property
    def text_metamodel(self):
        return self._tx_metamodel

    @property
    def last_valid_model(self):
        return self._last_valid_model

    @property
    def model_source(self):
        return self._model_source

    @property
    def exceptions(self):
        return self._exceptions

    @property
    def is_valid_model(self):
        return len(self.exceptions) == 0

    def try_parse_model(self, doc_source):
        try:
            # Problem when changing reference to another object in model
            self._metamodel = metamodel_from_file(config.GRAMMAR_PATH, debug=config.DEBUG)
            _model = self._metamodel.model_from_str(doc_source)
            self._last_valid_model = _model
            self._model_source = doc_source
            self._exceptions = []
            return _model
        except TextXError as e:
            msg = str(e).split(' at position')[0]
            e.message = msg
            # Currently TextX does not support error recovery
            # It will show first error in model
            
            # line = e.line
            # col = e.col
            # if (line,col) not in [(ex.line,ex.col) for ex in self._exceptions]:
            #     self._exceptions.append(e)
            self._exceptions = []
            self._exceptions.append(e)
            return None

    def get_rule_name_at_position(self, position):

        offset = _utils.line_col_to_pos(self.model_source, position)

        rules_dict = self.last_valid_model._pos_rule_dict
        
        rule = None
        for p in rules_dict.keys():
            if offset > p[0] and offset < p[1]:
                rule = rules_dict[p]
                break

        return rule


# Single instance
MODEL = Model()