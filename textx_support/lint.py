import _utils
import config
import model_processor

from lsp import Diagnostic

from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export, model_export
from textx.exceptions import TextXError

@_utils.debounce(config.LINT_DEBOUNCE_S)
def lint(doc_uri, workspace):
    if doc_uri in workspace.documents:
        diagnostic = Diagnostic()
        errors = model_processor.MODEL.all_errors
        for e in errors:
            msg = str(e)
            if msg.index(' at position') > 0:
                diagnostic.error(e.line, e.col, msg.split(' at position')[0])

        workspace.publish_diagnostics(doc_uri, diagnostic.get_diagnostics())
