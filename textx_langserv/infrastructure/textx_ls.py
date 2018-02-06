import logging
import hashlib
import os

from textx_langserv.utils import _utils, uris
from textx_langserv.infrastructure.language_server import LanguageServer
from textx_langserv.infrastructure.workspace import Workspace
from textx_langserv.infrastructure.configuration import Configuration

from textx_langserv.capabilities import get_capabilities

from textx_langserv.capabilities.completions import completions
from textx_langserv.capabilities.lint import lint
from textx_langserv.capabilities.hover import hover
from textx_langserv.capabilities.definitions import definitions
from textx_langserv.capabilities.find_references import find_all_references

from textx_langserv.commands import get_commands

from textx_langserv.infrastructure.dsl_handler import TxDslHandler

__author__ = "Daniel Elero"
__copyright__ = "textX-tools"
__license__ = "MIT"


log = logging.getLogger(__name__)


class TextXLanguageServer(LanguageServer):
    """
    Main class that wire all modules together
    """
    workspace = None
    configuration = None
    dsl_extension = None
    tx_dsl_handlers = {}

    commands = get_commands()

    def capabilities(self):
        return get_capabilities()

    def initialize(self, root_uri, init_opts, _process_id):
        self.process_id = _process_id
        self.root_uri = root_uri
        self.init_opts = init_opts

        self.workspace = Workspace(root_uri, self)
        self.configuration = Configuration(root_uri)

    def m_text_document__did_close(self, textDocument=None, **_kwargs):
        # Remove document from workspace
        self.workspace.rm_document(textDocument['uri'])
        # Remove handler from dict
        del self.tx_dsl_handlers[self.dsl_extension]

    def m_text_document__did_open(self, textDocument=None, **_kwargs):
        # Add document to workspace
        self.workspace.put_document(doc_uri=textDocument['uri'],
                                    content=textDocument['text'],
                                    version=textDocument.get('version'))
        # Add model handler in dict
        self.tx_dsl_handlers[self.dsl_extension] = \
            handler = TxDslHandler(self.configuration, self.dsl_extension)
        # Parse model and lint file
        self.tx_dsl_handlers[self.dsl_extension] \
            .parse_model(self.workspace.documents[textDocument['uri']].source)
        lint(textDocument['uri'], self.workspace, handler)

    def m_text_document__did_change(self,
                                    contentChanges=None,
                                    textDocument=None,
                                    **_kwargs):
        for change in contentChanges:
            self.workspace.update_document(
                textDocument['uri'],
                change,
                version=textDocument.get('version')
            )
        handler = self.tx_dsl_handlers[self.dsl_extension]
        handler.parse_model(
            self.workspace.documents[textDocument['uri']].source)
        lint(textDocument['uri'], self.workspace, handler)

    def m_text_document__did_save(self, textDocument=None, **_kwargs):
        handler = self.tx_dsl_handlers[self.dsl_extension]
        handler.parse_model(
            self.workspace.documents[textDocument['uri']].source)
        lint(textDocument['uri'], self.workspace, handler)

    def m_text_document__code_action(self, textDocument=None, range=None,
                                     context=None, **_kwargs):
        pass

    def m_text_document__code_lens(self, textDocument=None, **_kwargs):
        # return [{
        #     'range': {
        #         'start': {'line': 3, 'character': 2},
        #         'end': {'line': 3, 'character': 10}
        #     }
        # }]
        pass

    def m_text_document__completion(self, textDocument=None, position=None,
                                    **_kwargs):
        handler = self.tx_dsl_handlers[self.dsl_extension]
        handler.parse_model(
            self.workspace.documents[textDocument['uri']].source)
        model_source = self.workspace.get_document(textDocument['uri']).source
        return completions(model_source, position, handler)

    def m_text_document__definition(self, textDocument=None, position=None,
                                    **_kwargs):
        handler = self.tx_dsl_handlers[self.dsl_extension]
        handler.parse_model(
            self.workspace.documents[textDocument['uri']].source)
        return definitions(textDocument['uri'], position, handler)

    def m_text_document__hover(self, textDocument=None, position=None,
                               **_kwargs):
        handler = self.tx_dsl_handlers[self.dsl_extension]
        grammar_path = self.configuration.grammar_path
        return hover(textDocument['uri'], position, handler, grammar_path)

    def m_text_document__document_symbol(self, textDocument=None, **_kwargs):
        pass

    # def m_text_document__document_highlight(self, textDocument=None,
    #                                         **_kwargs):
    #     # return self.document_symbols(textDocument['uri'])
    #     pass

    def m_text_document__formatting(self, textDocument=None, options=None,
                                    **_kwargs):
        pass

    def m_text_document__range_formatting(self, textDocument=None, range=None,
                                          options=None, **_kwargs):
        pass

    def m_text_document__references(self, textDocument=None, position=None,
                                    context=None, **_kwargs):
        handler = self.tx_dsl_handlers[self.dsl_extension]
        handler.parse_model(
            self.workspace.documents[textDocument['uri']].source)
        return find_all_references(textDocument['uri'], position,
                                   context, handler)

    def m_text_document__signature_help(self, textDocument=None, position=None,
                                        **_kwargs):
        pass

    def m_workspace__did_change_configuration(self, settings=None):
        try:
            handler = self.tx_dsl_handlers[self.dsl_extension]
            for doc_uri in self.workspace.documents:
                lint(doc_uri, self.workspace, handler)
        except KeyError:
            pass

    def m_workspace__did_change_watched_files(self, **_kwargs):
        handler = self.tx_dsl_handlers[self.dsl_extension]
        for change in _kwargs['changes']:
            # Check if configuration file is changed
            if uris.to_fs_path(change['uri']) == \
                    self.configuration.txconfig_uri:
                loaded = self.configuration.load_configuration()
                if loaded:
                    self.workspace.show_message("You have to reopen your tabs \
                                                or restart vs code.")
                else:
                    self.workspace.show_message("Error in .txconfig file.")
            # TODO: Check if metamodel is changed

        # Externally changed files may result in changed diagnostics
        for doc_uri in self.workspace.documents:
            lint(doc_uri, self.workspace, handler)

    def m_workspace__execute_command(self, command=None, arguments=None):
        try:
            return self.commands[command](self, arguments)
        except KeyError:
            log.exception("Execute command error.")
            pass
