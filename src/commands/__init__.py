from src.utils.constants import TX_OUTLINE_COMMAND, \
    TX_METAMODEL_EXPORT_COMMAND, TX_MODEL_EXPORT_COMMAND, \
    TX_VSCODE_GENEXT_COMMAND

from .outline import OutlineTree
from .dotexport import dotexport_metamodel_cmd, \
    dotexport_model_cmd
from ..generators.vscode import vscode_generator

from threading import Thread


def get_commands():
    """
    Return dictionary with all registered commands
    NOTE:
        Be sure that command is registered in capabilities
    """
    return {
        TX_OUTLINE_COMMAND: _get_outline_command,
        TX_METAMODEL_EXPORT_COMMAND: dotexport_metamodel_cmd,
        TX_MODEL_EXPORT_COMMAND: dotexport_model_cmd,
        TX_VSCODE_GENEXT_COMMAND: _generate_vscode_ext_command
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


def _generate_vscode_ext_command(textx_ls, args):
    if textx_ls.gen_cmd_finished:
        thread = Thread(target=vscode_generator.generate,
                        args=(textx_ls, args, ))
        thread.start()
    else:
        msg = "You have already started generating."
        textx_ls.workspace.show_message(msg)
