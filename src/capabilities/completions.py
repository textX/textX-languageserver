from arpeggio import Match, EndOfFile

from textx.exceptions import TextXSemanticError, TextXSyntaxError
from textx.const import MULT_ASSIGN_ERROR, UNKNOWN_OBJ_ERROR
from textx.lang import BASE_TYPE_RULES

from ..utils import _utils
from ..infrastructure.lsp import Completions, CompletionItemKind

__author__ = "Daniel Elero"
__copyright__ = "textX-tools"
__license__ = "MIT"

# String to insert in model to make syntax errors
# MAKE SURE THAT STARTING CHAR IS NOT SAME AS COMMENT RULE:)
FAKE_SYN_CHARS = "&&^^&&)(A)21_"   # "#@#$(&!$"

# Do not offer these items
EXCLUDE_FROM_COMPLETIONS = ['Not', 'EOF', 'Comment']


def completions(doc_uri, workspace, position):
    """
    Returns completion items at current position.
    If model is valid, FAKE_SYN_CHARS are added to make parsing errors.
    """
    txdoc = workspace.get_document(doc_uri)

    if txdoc is None:
        return

    comps = Completions()
    offset = _utils.line_col_to_pos(txdoc.source, position)

    source = txdoc.source
    if txdoc.is_valid_model is True:
        source = txdoc.source[:offset] + FAKE_SYN_CHARS + \
            txdoc.source[offset:]

    # Parse invalid model and get errors
    syntax_errors, semantic_errors = \
        txdoc.parse_model(source, False)

    def get_syn_err_com_items(syntax_errors):
        items = []
        if len(syntax_errors) > 0:
            # Arrpegio currently returns just one error
            err = syntax_errors[0]
            items.extend(
                [rule_to_exp_str(r)
                    for r in err.expected_rules
                    if rule_to_exp_str(r) not in EXCLUDE_FROM_COMPLETIONS])

        # Check ID
        if len(items) > 0 and items[0] == 'ID':
            rule = txdoc.get_rule_inst_at_position(position)
            if rule is not None:
                _, meta_attr = first_from_ordered_dict(type(rule)._tx_attrs)
                if meta_attr.ref:
                    insts = _get_instances_of_cls(meta_attr.cls)
                    items.extend(insts)
        return items

    def get_sem_err_com_items(semantic_errors):
        items = []
        if len(semantic_errors) > 0:
            for e in semantic_errors:
                if e.err_type == UNKNOWN_OBJ_ERROR:
                    # If type of error is UNKNOWN_OBJ_ERROR
                    # Find all instances of expected class
                    # and offer their name attribute
                    if txdoc.last_valid_model is None:
                        return []

                    items.extend(_get_instances_of_cls(e.expected_obj_cls))

                elif e.err_type == MULT_ASSIGN_ERROR:
                    pass

        return items

    def _get_instances_of_cls(cls):
        def _get_parent_classes(cls):
            ret_val = []
            ret_val.append(cls.__name__)
            try:
                ret_val.extend([c.__name__
                                for c
                                in cls._tx_inh_by
                                if hasattr(c, '__name__')])
            except:
                pass

            return ret_val

        cls_names = []
        cls_names.extend(_get_parent_classes(cls))
        instances = []
        instances.extend([obj.name
                          for obj in txdoc.get_all_rule_instances()
                          if hasattr(obj, 'name') and
                          type(obj).__name__ in cls_names])
        return instances

    for i in get_syn_err_com_items(syntax_errors):
        comps.add_completion(i)

    for i in get_sem_err_com_items(semantic_errors):
        comps.add_completion(i)

    return {
        'isIncomplete': False,
        'items': comps.get_completions()
    }


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


def first_from_ordered_dict(od):
    if isinstance(od, dict):
        first_key = next(iter(od))
        first_value = od[first_key]
        return first_key, first_value
