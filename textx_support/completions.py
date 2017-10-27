import config
import model_processor
from lsp import Completions, CompletionItemKind

from textx.exceptions import TextXSemanticError, TextXSyntaxError
from textx.const import MULT_ASSIGN_ERROR, UNKNOWN_OBJ_ERROR

def completions(model_source, position):
    completions = Completions()
    model = model_processor.MODEL

    try:
        parsed_model = model.parse_model(model_source)
        # If parsed model is valid make an error
        # to get possible rules at current position
        # and parse model again to get exception

    except TextXSemanticError as e:
        # If type of error is UNKNOWN_OBJ_ERROR
        # Find all instances of expected class
        # and offer their name attribute
        pass

    except TextXSyntaxError as e:
        # If one of possible rules are reference to other object
        # try to fix syntax error and raise semantic error
        pass

    # return {
    #     'isIncomplete': False,
    #     'items': completions.get_completions()
    # }