from utils import _utils
from infrastructure.lsp import Diagnostic

from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export, model_export
from textx.exceptions import TextXError

LINT_DEBOUNCE_S = 0.5

@_utils.debounce(LINT_DEBOUNCE_S)
def lint(doc_uri, workspace, tx_dsl_handler):
    if doc_uri in workspace.documents:
        diagnostic = Diagnostic()
        errors = tx_dsl_handler.all_errors
        for e in errors:
            msg = str(e)
            try:
                msg = msg.split(' at')[0]
                diagnostic.error(e.line, e.col, msg)
            except:
                diagnostic.error(e.line, e.col, msg)

        workspace.publish_diagnostics(doc_uri, diagnostic.get_diagnostics())
