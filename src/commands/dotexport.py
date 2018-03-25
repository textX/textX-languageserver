import uuid

from os.path import join, basename, splitext
from textx import metamodel_from_file
from textx.export import metamodel_export, model_export
from ..utils.uris import to_fs_path


def dotexport_metamodel_cmd(textx_ls, args):
    """
    Exports metamodel to workspace (dot file)
    """
    ws_path = to_fs_path(textx_ls.root_uri)

    metamodel_path = textx_ls.configuration.grammar_path
    mm = metamodel_from_file(metamodel_path)
    mm_file_name = splitext(basename(metamodel_path))[0] or uuid.uuid4().hex

    path = join(ws_path, mm_file_name + '_metamodel.dot')
    metamodel_export(mm, path)
    textx_ls.workspace.show_message("Metamodel is exported at {}".format(path))


def dotexport_model_cmd(textx_ls, args):
    """
    Exports all valid models from current opened tabs (dot file(s))
    """
    ws_path = to_fs_path(textx_ls.root_uri)

    docs = textx_ls.workspace.documents

    if len(docs) == 0:
        textx_ls.workspace.show_message("Open model you want to export")
        return

    for d in list(docs.values()):
        if d.is_valid_model:
            file_name = d.filename.replace('.', '_') or uuid.uuid4().hex
            path = join(ws_path, file_name + '_model.dot')
            model_export(d.last_valid_model, path)
            textx_ls.workspace.show_message("Model is exported at {}"
                                            .format(path))
