"""
This module is responsible for go to definition feature.
"""
import bisect

from ..utils import _utils

__author__ = "Daniel Elero"
__copyright__ = "textX-tools"
__license__ = "MIT"


def definitions(doc_uri, workspace, position):
    """
    If cursor position is on the reference to other instance of rule
    Go to definition will place the cursor at the begining of referenced rule

    - Binary searching the list of all references in model
    - Currently TextX supports only one file per model, so the referenced rule
    - must be in the same file
    - Don't forget builtins
    """

    txdoc = workspace.get_document(doc_uri)
    if txdoc is not None and txdoc.is_valid_model:

        source = txdoc.source

        offset = _utils.line_col_to_pos(source, position)

        # List of all references in model
        crossref_list = txdoc.last_valid_model._pos_crossref_list

        # Find offset that is in range of ref_pos_start and ref_pos_end
        ref_rule = None

        # Binary search the list
        ref_rule = find(offset, crossref_list)

        if ref_rule is None:
            return

        # Get positions for definition of referenced rule
        st_line, st_col = _utils.pos_to_line_col(source,
                                                 ref_rule.def_pos_start)
        end_line, end_col = _utils.pos_to_line_col(source,
                                                   ref_rule.def_pos_end)

        return [{
            'uri': doc_uri,
            'range': {
                'start': {'line': st_line, 'character': st_col},
                'end': {'line': end_line, 'character': end_col}
            }
        }]


def find(offset, sorted_list):
    """
    Binary search the sorted list
    Offset has to be between starting and ending position of reference
    """
    idx = bisect.bisect([ref_obj.ref_pos_start
                         for ref_obj in sorted_list], offset) - 1
    if idx < 0:
        return None
    ref_obj = sorted_list[idx]
    return ref_obj if ref_obj.ref_pos_end >= offset else None
