from textx_langserv.utils.constants import TX_OUTLINE_COMMAND, \
    TX_METAMODEL_EXPORT_COMMAND, TX_MODEL_EXPORT_COMMAND

from textx_langserv.commands.outline import OutlineTree
from textx_langserv.commands.dotexport import dotexport_metamodel_cmd, \
    dotexport_model_cmd


def get_commands():
    """
    Return dictionary with all registered commands
    NOTE:
        Be sure that command is registered in capabilities
    """
    return {
        TX_OUTLINE_COMMAND: _get_outline_command,
        TX_METAMODEL_EXPORT_COMMAND: dotexport_metamodel_cmd,
        TX_MODEL_EXPORT_COMMAND: dotexport_model_cmd
    }


def _get_outline_command(textx_ls, args):
    try:
        txdoc = textx_ls.workspace.get_document(args[0]['uri']['external'])
        if txdoc is not None:
            return OutlineTree(
                    model_source=txdoc.source,
                    outline_model=textx_ls.configuration.outline_model,
                    current_model=txdoc.last_valid_model
                   ).make_tree()
    except:
        pass
