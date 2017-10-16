import model_processor
import _utils

def definitions(doc_uri, position):
    model = model_processor.MODEL

    if model.is_valid_model:

        rule_name, model_obj = model.get_rule_name_at_position(position)
        
        # Get word under the cursor
        source = model.model_source
        word = _utils.get_ident_at_position(source, position)

        # 
        st_pos = 0
        end_pos = 0

        # Get model attributes
        attr_names = type(model_obj)._tx_attrs.keys()

        # Itterate model attributes and find referenced object
        for attr in attr_names:
            temp = getattr(model_obj, attr)
            if isinstance(temp, list):
                for t in temp:
                    # If rule is referenced, does it always have the "name" attr?
                    if hasattr(t, 'name') and t.name == word:
                        st_pos = t._tx_position
                        end_pos = t._tx_position_end
            else:
                if hasattr(temp, 'name') and temp.name == word:
                    st_pos = temp._tx_position
                    end_pos = temp._tx_position_end
        
        if st_pos == 0:
            return
    
        st_line, st_col = _utils.pos_to_line_col(source, st_pos)
        end_line, end_col = _utils.pos_to_line_col(source, end_pos)        

        return [{
            'uri': doc_uri,
            'range': {
                'start': {'line': st_line, 'character': st_col},
                'end': {'line': end_line, 'character': end_col}
            }
        }]