import model_processor
import _utils

def definitions(doc_uri, position):
    model = model_processor.MODEL

    if model.is_valid_model:

        source = model.model_source
        
        offset = _utils.line_col_to_pos(source, position)
        
        # Find referenced rule in dict
        crossref_dict = model.last_valid_model._pos_crossref_dict

        ref_rule = None
        for p in crossref_dict.keys():
            if offset > p and offset < crossref_dict[p].pos_end:
                ref_rule = crossref_dict[p]

        if ref_rule is None:
            return

        st_line, st_col = _utils.pos_to_line_col(source, ref_rule.rule_pos_start)
        end_line, end_col = _utils.pos_to_line_col(source, ref_rule.rule_pos_end)
       
        return [{
            'uri': doc_uri,
            'range': {
                'start': {'line': st_line, 'character': st_col},
                'end': {'line': end_line, 'character': end_col}
            }
        }]