from textx_langserv.utils.constants import TX_OUTLINE_COMMAND

from textx_langserv.commands.outline import OutlineTree


def get_commands():
    """
    Return dictionary with all registered commands
    NOTE:
        Be sure that command is registered in capabilities
    """
    return {
        TX_OUTLINE_COMMAND: _get_outline_command
    }


def _get_outline_command(textx_ls, args):
    try:
        handler = textx_ls.tx_dsl_handlers[textx_ls.dsl_extension]
        if handler is not None:
            return OutlineTree(
                    model_source=handler.model_source,
                    outline_model=textx_ls.configuration.outline_model,
                    current_model=handler.last_valid_model
                   ).make_tree()
    except:
        pass
