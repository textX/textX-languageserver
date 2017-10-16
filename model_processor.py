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
        line = position['line']
        col = position['character']
        pos = _utils.line_col_to_pos(self._model_source,line,col)
        model = self.last_valid_model

        # Find rule name at current position
        rule_name, model_obj = self._find_rule_name_at_position(model, pos)
        return rule_name, model_obj

    def _find_rule_name_at_position(self, model_obj, pos):
        """
        Depth-first model object processing.
        """
        metaclass = type(model_obj)
        if type(model_obj) not in PRIMITIVE_PYTHON_TYPES:
            for metaattr in metaclass._tx_attrs.values():
                # If attribute is containment reference go down
                if metaattr.ref and metaattr.cont:
                    attr = getattr(model_obj, metaattr.name)
                    if attr:
                        if metaattr.mult != MULT_ONE:
                            for obj in attr:
                                if obj:
                                    ret = self._find_rule_name_at_position(obj, pos)
                                    if ret is not None:
                                        return ret
                        else:
                            ret = self._find_rule_name_at_position(attr, pos)
                            if ret is not None:
                                return ret

        if hasattr(model_obj, '_tx_position'):
            if model_obj._tx_position <= pos and model_obj._tx_position_end >= pos:
                return metaclass.__name__, model_obj


# Single instance
MODEL = Model()