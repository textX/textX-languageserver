from ..utils._utils import pos_to_line_col

REFERENCE_TEXT_LENS = "{0} references"


def code_lens(doc_uri, workspace):

    txdoc = workspace.get_document(doc_uri)
    if txdoc is not None and txdoc.is_valid_model:
        # List of all references in model

        try:
            crossref_list = txdoc.last_valid_model._pos_crossref_list
        except:
            return

        def count_references(crossref_list):
            # Key: rule name + def position start + def position end
            # Value: (ref count, (def_pos_start_line, def_pos_start_col),
            #                    (def_pos_end_line, def_pos_end_col))
            rule_ref_dict = {}

            for ref in crossref_list:
                key = '{}{}{}'.format(ref.name,
                                      ref.def_pos_start,
                                      ref.def_pos_end)
                try:
                    ref_count, def_pos_start, def_pos_end = \
                        rule_ref_dict[key]
                    ref_count += 1
                    rule_ref_dict[key] = (ref_count,
                                          def_pos_start,
                                          def_pos_end)
                except:
                    rule_ref_dict[key] = (1,
                                          pos_to_line_col(
                                            txdoc.source,
                                            ref.def_pos_start),
                                          pos_to_line_col(
                                            txdoc.source,
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
                            'command': 'code_lens_references',
                            'arguments': [
                                    def_pos_start[0],       # line
                                    def_pos_start[1] + 1,   # character
                            ]
                        }
                    } for ref_count, def_pos_start, def_pos_end in
                    rule_ref_dict.values()]

        ret_val = []
        ret_val.extend(get_references_lens(rule_ref_dict))

        return ret_val
