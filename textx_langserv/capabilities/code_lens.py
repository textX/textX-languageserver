from textx_langserv.utils._utils import pos_to_line_col

REFERENCE_TEXT_LENS = "{0} references"


def code_lens(model_source, tx_dsl_handler):

    if tx_dsl_handler.is_valid_model:
        # List of all references in model

        crossref_list = tx_dsl_handler.last_valid_model._pos_crossref_list

        def count_references(crossref_list):
            # Key: rule name
            # Value: (ref count, (def_pos_start_line, def_pos_start_col),
            #                    (def_pos_end_line, def_pos_end_col))
            rule_ref_dict = {}

            for ref in crossref_list:
                try:
                    ref_count, def_pos_start, def_pos_end = \
                        rule_ref_dict[ref.name]
                    ref_count += 1
                    rule_ref_dict[ref.name] = (ref_count,
                                               def_pos_start,
                                               def_pos_end)
                except:
                    rule_ref_dict[ref.name] = (1,
                                               pos_to_line_col(
                                                   model_source,
                                                   ref.def_pos_start),
                                               pos_to_line_col(
                                                   model_source,
                                                   ref.def_pos_end
                                               ))
            return rule_ref_dict

        rule_ref_dict = count_references(crossref_list)

        def get_references_lens(rule_ref_dict):
            """
            Show references in code lens
            If there are additional commands in code lens,
            create class for code lens items.
            """
            return [{
                        'range': {
                            'start': {
                                'line': def_pos_start[0],
                                'character': def_pos_start[1]
                            },
                            'end': {
                                'line': def_pos_end[0],
                                'character': def_pos_end[1]
                            }
                        },
                        'command': {
                            'title': REFERENCE_TEXT_LENS.format(ref_count),
                            # 'command': 'LENS_REFERENCES'
                        }
                    } for ref_count, def_pos_start, def_pos_end in
                    rule_ref_dict.values()]

        ret_val = []
        ret_val.extend(get_references_lens(rule_ref_dict))

        return ret_val
