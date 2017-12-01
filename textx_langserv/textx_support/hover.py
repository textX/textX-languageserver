from textx_langserv import config, model_processor


model_proc = model_processor.MODEL_PROCESSOR
def hover(doc_uri, position):

    # rule = model_proc.get_rule_at_position(position)
    # if rule is None:
    #     return

    # with open(config.GRAMMAR_PATH, 'r') as mm_file:
    #     content = mm_file.read()[rule._tx_position:rule._tx_position_end]
    #     return {'contents': content}
    pass