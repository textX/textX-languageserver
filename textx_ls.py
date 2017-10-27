import logging
import lsp, _utils, uris
from language_server import LanguageServer
from workspace import Workspace

import config
import model_processor

from os.path import join, dirname


from textx_support.completions import completions
from textx_support.lint import lint
from textx_support.hover import hover
from textx_support.definitions import definitions



log = logging.getLogger(__name__)

class TextXLanguageServer(LanguageServer):

    workspace = None

    def capabilities(self):
        return {
            'codeActionProvider': True,
            'codeLensProvider': {
                'resolveProvider': False,
            },
            'completionProvider': {
                'resolveProvider': False,
                'triggerCharacters': ['.']
            },
            'documentFormattingProvider': True,
            'documentRangeFormattingProvider': True,
            'documentSymbolProvider': True,
            'definitionProvider': True,
            'executeCommandProvider': {
                'commands': []
            },
            'hoverProvider': True,
            'referencesProvider': True,
            'signatureHelpProvider': {
                'triggerCharacters': ['(', ',']
            },
            'textDocumentSync': lsp.TextDocumentSyncKind.INCREMENTAL
        }

    def initialize(self, root_uri, init_opts, _process_id):
        self.workspace = Workspace(root_uri, lang_server=self)

    def code_actions(self, doc_uri, range, context):
        pass

    def code_lens(self, doc_uri):
        pass

    def document_symbols(self, doc_uri):
        pass

    def execute_command(self, command, arguments):
        pass

    def format_document(self, doc_uri):
        pass

    def format_range(self, doc_uri, range):
        pass

    def references(self, doc_uri, position, exclude_declaration):
        pass

    def signature_help(self, doc_uri, position):
        pass

    def m_text_document__did_close(self, textDocument=None, **_kwargs):
        self.workspace.rm_document(textDocument['uri'])

    def m_text_document__did_open(self, textDocument=None, **_kwargs):
        self.workspace.put_document(textDocument['uri'], textDocument['text'], version=textDocument.get('version'))
        model_processor.MODEL.parse_model(self.workspace.documents[textDocument['uri']].source)
        lint(textDocument['uri'], self.workspace)

    def m_text_document__did_change(self, contentChanges=None, textDocument=None, **_kwargs):
        for change in contentChanges:
            self.workspace.update_document(
                textDocument['uri'],
                change,
                version=textDocument.get('version')
            )
        model_processor.MODEL.parse_model(self.workspace.documents[textDocument['uri']].source)
        lint(textDocument['uri'], self.workspace)

    def m_text_document__did_save(self, textDocument=None, **_kwargs):
        lint(textDocument['uri'], self.workspace)

    def m_text_document__code_action(self, textDocument=None, range=None, context=None, **_kwargs):
        return self.code_actions(textDocument['uri'], range, context)

    def m_text_document__code_lens(self, textDocument=None, **_kwargs):
        return self.code_lens(textDocument['uri'])

    def m_text_document__completion(self, textDocument=None, position=None, **_kwargs):
        model_source = self.workspace.get_document(textDocument['uri']).source
        return completions(model_source, position)

    def m_text_document__definition(self, textDocument=None, position=None, **_kwargs):
        return definitions(textDocument['uri'], position)

    def m_text_document__hover(self, textDocument=None, position=None, **_kwargs):
        return hover(textDocument['uri'], position)

    def m_text_document__document_symbol(self, textDocument=None, **_kwargs):
        return self.document_symbols(textDocument['uri'])

    def m_text_document__formatting(self, textDocument=None, options=None, **_kwargs):
        # For now we're ignoring formatting options.
        return self.format_document(textDocument['uri'])

    def m_text_document__range_formatting(self, textDocument=None, range=None, options=None, **_kwargs):
        # Again, we'll ignore formatting options for now.
        return self.format_range(textDocument['uri'], range)

    def m_text_document__references(self, textDocument=None, position=None, context=None, **_kwargs):
        exclude_declaration = not context['includeDeclaration']
        return self.references(textDocument['uri'], position, exclude_declaration)

    def m_text_document__signature_help(self, textDocument=None, position=None, **_kwargs):
        return self.signature_help(textDocument['uri'], position)

    def m_workspace__did_change_configuration(self, settings=None):
        for doc_uri in self.workspace.documents:
            lint(doc_uri, self.workspace)

    def m_workspace__did_change_watched_files(self, **_kwargs):
        # Externally changed files may result in changed diagnostics
        for doc_uri in self.workspace.documents:
            lint(doc_uri, self.workspace)

    def m_workspace__execute_command(self, command=None, arguments=None):
        return self.execute_command(command, arguments)
