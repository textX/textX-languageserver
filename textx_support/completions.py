import config
import model_processor
from lsp import Completions, CompletionItemKind

from textx.exceptions import TextXSemanticError, TextXSyntaxError
from textx.const import MULT_ASSIGN_ERROR, UNKNOWN_OBJ_ERROR

def completions(model_source, position):
    completions = Completions()
    model_proc = model_processor.MODEL_PROCESSOR
    last_valid_model = model_proc.last_valid_model

    # List of strings that should be in completion list   
    items = []

    if model_proc.is_valid_model:
        # If parsed model is valid make an error
        # to get possible rules at current position
        # and parse model again to get exception
        pass
    else:
        if model_proc.has_syntax_errors:
            # If one of expected rules are reference to other object
            # try to fix syntax error and raise semantic error
            pass

        if model_proc.has_semantic_errors:
            for e in model_proc.semantic_errors:
                if e.err_type == UNKNOWN_OBJ_ERROR:
                    # If type of error is UNKNOWN_OBJ_ERROR
                    # Find all instances of expected class
                    # and offer their name attribute
                    def _find_instances_of_class(cls):
                        if last_valid_model is None:
                            return []

                        return [obj.name
                            for obj in last_valid_model._pos_rule_dict.values()
                            if hasattr(obj,'name') and type(obj).__name__ == cls.__name__]

                    instance_names = _find_instances_of_class(e.expected_obj_cls)
                    items.extend(instance_names)

                if e.err_type == MULT_ASSIGN_ERROR:
                    pass
            pass

    for i in items:
        completions.add_completion(i)

    return {
        'isIncomplete': False,
        'items': completions.get_completions()
    }