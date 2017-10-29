import config
import model_processor
from lsp import Completions, CompletionItemKind

from textx.exceptions import TextXSemanticError, TextXSyntaxError
from textx.const import MULT_ASSIGN_ERROR, UNKNOWN_OBJ_ERROR
from textx.lang import BASE_TYPE_RULES

from arpeggio import Match, EndOfFile

import _utils

# Dictionary for random rule matches
FAKE_RULE_MATCHES = {
    "ID" : " aaaBBBcccDDDeeeFFFgggHHHiiiJJJkkkLLLmmmNNN "
}

# String to insert in model to make parsing errors
FAKE_SYN_CHARS = "#@#$(&!$"

# 
MAX_RECURSION_CALLS = 20

# Do not offer these items
EXCLUDE_FROM_COMPLETIONS = ['Not', 'EOF']

def completions(model_source, position):
    """
    Returns completion items at current position.
    If model is valid, FAKE_SYN_CHARS are added to make parsing errors.
    """

    comps = Completions()
    model_proc = model_processor.MODEL_PROCESSOR
    last_valid_model = model_proc.last_valid_model

    offset = _utils.line_col_to_pos(model_source, position)

    # If model is valid, create fake model
    if model_proc.is_valid_model:
        model_source = model_source[:offset] + FAKE_SYN_CHARS + model_source[offset:]


    def _get_completions(model_source, offset):
        """
        Params:
            model_source(string): File that contains model - always invalid
            offset(int): Cursor position offset
        Returns:
            items(list): List of strings (completion items)
        """

        # recursion counter
        _get_completions.rcounter += 1

        # Parse fake model and get errors
        syntax_errors, semantic_errors = model_proc.fake_parse_model(model_source)

        # Remove fake string which is added to make errors
        model_source = model_source.replace(FAKE_SYN_CHARS,'')

        # If error type is TextXSemanticError
        if len(semantic_errors) > 0:
            for e in semantic_errors:
                if e.err_type == UNKNOWN_OBJ_ERROR:
                    # If type of error is UNKNOWN_OBJ_ERROR
                    # Find all instances of expected class
                    # and offer their name attribute
                    if last_valid_model is None:
                        return []

                    return [obj.name
                        for obj in last_valid_model._pos_rule_dict.values()
                        if hasattr(obj,'name') and type(obj).__name__ == e.expected_obj_cls.__name__]

                elif e.err_type == MULT_ASSIGN_ERROR:
                    # Find out what to do here
                    pass

        # If error type is TextXSyntaxError
        if len(syntax_errors) > 0:
            # Arrpegio currently returns just one error
            err = syntax_errors[0]

            # Coppied from arpeggio
            def rule_to_exp_str(rule):
                if hasattr(rule, '_exp_str'):
                    # Rule may override expected report string
                    return rule._exp_str
                elif rule.root:
                    return rule.rule_name
                elif isinstance(rule, Match) and \
                        not isinstance(rule, EndOfFile):
                    return rule.to_match
                else:
                    return rule.name


            # If it's not possible to make semantic errors save first expected rule matches
            if len(_get_completions.items) == 0:
                _get_completions.items.extend([rule_to_exp_str(r) for r in err.expected_rules
                        if rule_to_exp_str(r) not in EXCLUDE_FROM_COMPLETIONS ])
            
            # Return items if max recursion calls are reached
            if _get_completions.rcounter == MAX_RECURSION_CALLS:
                return _get_completions.items
            
            # Try to make valid string to get semantic error if possible
            # Add random rule match to model source and invoke _get_completions
            # with a new fake model and offset
            # TODO: Add other fake rule matches (regex,int,...)
            for e in err.expected_rules:
                str_to_add = ''
                if hasattr(e,'rule_name'):
                    if e.rule_name in FAKE_RULE_MATCHES.keys():
                        str_to_add = FAKE_RULE_MATCHES[e.rule_name]
                    elif hasattr(e,'to_match') and e.rule_name.strip() == '':
                        str_to_add = e.to_match
                    else:
                        # ?
                        str_to_add = FAKE_RULE_MATCHES["ID"]

                if str_to_add != '':
                    new_model_source = model_source[:offset] + str_to_add + model_source[offset:]
                    return _get_completions(new_model_source, offset + len(str_to_add))

            return _get_completions.items


    # Init
    _get_completions.rcounter = 0
    _get_completions.items = []

    items = _get_completions(model_source, offset)

    for i in items:
        comps.add_completion(i)

    return {
        'isIncomplete': False,
        'items': comps.get_completions()
    }