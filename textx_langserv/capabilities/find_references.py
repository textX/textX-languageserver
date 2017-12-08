from utils import _utils
import bisect

def find_all_references(doc_uri, position, context, tx_dsl_handler):
    """
    """
    if tx_dsl_handler.is_valid_model:

        source = tx_dsl_handler.model_source
        
        offset = _utils.line_col_to_pos(source, position)
        
        # List of all references in model
        crossref_list = tx_dsl_handler.last_valid_model._pos_crossref_list

        all_references = []
        for ref_rule in crossref_list:
            if ref_rule.def_pos_end > offset > ref_rule.def_pos_start:
                st_line, st_col = _utils.pos_to_line_col(source, ref_rule.ref_pos_start)
                end_line, end_col = _utils.pos_to_line_col(source, ref_rule.ref_pos_end)
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