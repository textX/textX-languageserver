import logging
import hashlib
import os

from utils import _utils, uris
from infrastructure import lsp
from infrastructure.language_server import LanguageServer
from infrastructure.workspace import Workspace
from infrastructure.configuration import Configuration

from capabilities.completions import completions
from capabilities.lint import lint
from capabilities.hover import hover
from capabilities.definitions import definitions
from capabilities.find_references import find_all_references

from infrastructure.dsl_handler import TxDslHandler

log = logging.getLogger(__name__)

class TextXLanguageServer(LanguageServer):

    workspace = None
    configuration = None


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
            # 'documentHighlightProvider': True,
            'documentRangeFormattingProvider': True,
            'documentSymbolProvider': True,
            'definitionProvider': True,
            'executeCommandProvider': {
                'commands': ['genext','corefresh', 'test']
            },
            'hoverProvider': True,
            'referencesProvider': True,
            'signatureHelpProvider': {
                'triggerCharacters': ['(', ',']
            },
            'textDocumentSync': lsp.TextDocumentSyncKind.INCREMENTAL
        }


    def initialize(self, root_uri, init_opts, _process_id):
        self.process_id = _process_id
        self.root_uri = root_uri
        self.init_opts = init_opts

        self.workspace = Workspace(root_uri, self)
        self.tx_dsl_handler = TxDslHandler()
        self.configuration = Configuration(root_uri)


    def m_text_document__did_close(self, textDocument=None, **_kwargs):
        self.workspace.rm_document(textDocument['uri'])

    def m_text_document__did_open(self, textDocument=None, **_kwargs):
        self.workspace.put_document(textDocument['uri'], textDocument['text'], version=textDocument.get('version'))
        self.tx_dsl_handler.parse_model(self.workspace.documents[textDocument['uri']].source)
        lint(textDocument['uri'], self.workspace, self.tx_dsl_handler)

    def m_text_document__did_change(self, contentChanges=None, textDocument=None, **_kwargs):
        for change in contentChanges:
            self.workspace.update_document(
                textDocument['uri'],
                change,
                version=textDocument.get('version')
            )
        self.tx_dsl_handler.parse_model(self.workspace.documents[textDocument['uri']].source)
        lint(textDocument['uri'], self.workspace, self.tx_dsl_handler)

    def m_text_document__did_save(self, textDocument=None, **_kwargs):
        self.tx_dsl_handler.parse_model(self.workspace.documents[textDocument['uri']].source)
        lint(textDocument['uri'], self.workspace, self.tx_dsl_handler)

    def m_text_document__code_action(self, textDocument=None, range=None, context=None, **_kwargs):
        pass

    def m_text_document__code_lens(self, textDocument=None, **_kwargs):
        pass

    def m_text_document__completion(self, textDocument=None, position=None, **_kwargs):
        self.tx_dsl_handler.parse_model(self.workspace.documents[textDocument['uri']].source)
        model_source = self.workspace.get_document(textDocument['uri']).source
        return completions(model_source, position, self.tx_dsl_handler)

    def m_text_document__definition(self, textDocument=None, position=None, **_kwargs):
        self.tx_dsl_handler.parse_model(self.workspace.documents[textDocument['uri']].source)
        return definitions(textDocument['uri'], position, self.tx_dsl_handler)

    def m_text_document__hover(self, textDocument=None, position=None, **_kwargs):
        return hover(textDocument['uri'], position, self.tx_dsl_handler)

    def m_text_document__document_symbol(self, textDocument=None, **_kwargs):
        pass
    
    # def m_text_document__document_highlight(self, textDocument=None, **_kwargs):
    #     # return self.document_symbols(textDocument['uri'])
    #     pass

    def m_text_document__formatting(self, textDocument=None, options=None, **_kwargs):
        pass

    def m_text_document__range_formatting(self, textDocument=None, range=None, options=None, **_kwargs):
        pass

    def m_text_document__references(self, textDocument=None, position=None, context=None, **_kwargs):
        pass
        

    def m_text_document__signature_help(self, textDocument=None, position=None, **_kwargs):
        pass

    def m_workspace__did_change_configuration(self, settings=None):
        for doc_uri in self.workspace.documents:
            lint(doc_uri, self.workspace, self.tx_dsl_handler)

    def m_workspace__did_change_watched_files(self, **_kwargs):
        for change in _kwargs['changes']:
            if uris.to_fs_path(change['uri']) == self.configuration.txconfig_uri:
                self.configuration.update_configuration()
                self.workspace.show_message("You have to reopen your tabs or restart vs code.")
        # Externally changed files may result in changed diagnostics
        for doc_uri in self.workspace.documents:
            lint(doc_uri, self.workspace, self.tx_dsl_handler)
        

    def m_workspace__execute_command(self, command=None, arguments=None):
        print(command)
        #return [1,2,3,4,5]
