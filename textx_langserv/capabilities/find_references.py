"""
This module is responsible for find all references feature.
"""
import bisect

from textx_langserv.utils import _utils

__author__ = "Daniel Elero"
__copyright__ = "textX-tools"
__license__ = "MIT"


def find_all_references(doc_uri, position, context, tx_dsl_handler):
    """
    Iterates crossref list and store all rules that meet the
    condition
    """
    if tx_dsl_handler.is_valid_model:

        source = tx_dsl_handler.model_source

        # List of all references in model
        crossref_list = tx_dsl_handler.last_valid_model._pos_crossref_list

        rule = tx_dsl_handler.get_rule_at_position(position)

        all_references = []
        for ref_rule in crossref_list:
            if ref_rule.def_pos_start == rule._tx_position and \
               ref_rule.def_pos_end == rule._tx_position_end:
                st_line, st_col = _utils.pos_to_line_col(
                                    source, ref_rule.ref_pos_start)
                end_line, end_col = _utils.pos_to_line_col(
                                        source, ref_rule.ref_pos_end)
                all_references.append((
                    (st_line, st_col), (end_line, end_col)
                ))

        return [{
            'uri': doc_uri,
            'range': {
                'start': {'line': ref[0][0], 'character': ref[0][1]},
                'end': {'line': ref[1][0], 'character': ref[1][1]}
            }
        } for ref in all_references]