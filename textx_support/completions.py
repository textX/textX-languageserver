import config
import model_processor
from lsp import Completions, CompletionItemKind

def completions(position):
    completions = Completions()
    model = model_processor.MODEL

    if model.is_valid_model:
        rule_name, model_obj = model.get_rule_name_at_position(position)
        print(rule_name)

        # mm = model.metamodel
        # txmm = model.text_metamodel
        # m = txmm.model_from_file(config.GRAMMAR_PATH)

        # # completions.add_completion('ins', CompletionItemKind.Snippet, 2, 'insert $1')
        # import pprint
        # p = pprint.pprint

        # rule = None
        # for r in m.rules:
        #     if r.name == rule_name:
        #         rule = r
        #         break
        
        # if rule is not None:
        #     p(rule.body.expr.__dict__)

        # meta = type(model_obj)
        # for key in meta._tx_attrs.keys():
        #     print("---------------------------------------------------------------------------------")
        #     p(meta._tx_attrs[key].cls.__dict__)
        


        # TODO
        # Get rule in metamodel
        # Parse metamodel with textx grammar
        # Get information of rule and make completion list

        # For each metamodel attribute, check if model already has it - if mandatory

        # Dinamicaly create snippet, if not already created (keep it in dictionary)
        # Get simple match string and right side assignments

    else:
        # Parse textx error message and create completions
        for e in model.exceptions:
            for c in parse_error_message(e):
                completions.add_completion(c)

    return {
        'isIncomplete': False,
        'items': completions.get_completions()
    }


def parse_error_message(ex):
    expected = str(ex).split('Expected ')[1].split(' at position')[0]
    import re
    return re.findall(r"\'(.+?)\'", expected)