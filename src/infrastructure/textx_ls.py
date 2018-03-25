import logging
import hashlib
import os

from os.path import join

from ..utils.constants import SERVER_TYPE, SERVER_CONNECTION,\
    SERVER_GENERAL, SERVER_PIPES, SERVER_TCP
from ..utils import _utils, uris

from ..infrastructure.language_server import LanguageServer
from ..infrastructure.workspace import Workspace
from ..infrastructure.configuration import Configuration
from ..infrastructure.lsp import MessageType

from ..capabilities import get_capabilities
from ..capabilities.completions import completions
from ..capabilities.lint import lint
from ..capabilities.hover import hover
from ..capabilities.definitions import definitions
from ..capabilities.find_references import find_all_references
from ..capabilities.code_lens import code_lens

from ..commands import get_commands

from .. import LS_ROOT_PATH

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

    commands = get_commands()

    def capabilities(self):
        cmd_list = list(self.commands.keys())
        return get_capabilities(cmd_list)

    def initialize(self, root_uri, init_opts, _process_id):
        self.process_id = _process_id
        self.root_uri = root_uri

        self.server_type = init_opts[SERVER_TYPE]
        self.server_connection = init_opts[SERVER_CONNECTION]

        self.gen_cmd_finished = True

        self.workspace = Workspace(root_uri, self)

        # Change config uri for generated extensions
        config_root_uri = uris.to_fs_path(root_uri)
        if self.server_type != SERVER_GENERAL:
            config_root_uri = join(LS_ROOT_PATH, 'txconfig')

        self.configuration = Configuration(config_root_uri)

    def m_text_document__did_close(self, textDocument=None, **_kwargs):
        # Remove document from workspace
        self.workspace.rm_document(textDocument['uri'])

    def m_text_document__did_open(self, textDocument=None, **_kwargs):
        # Add document to workspace
        self.workspace.put_document(doc_uri=textDocument['uri'],
                                    content=textDocument['text'],
                                    version=textDocument.get('version'))
        lint(textDocument['uri'], self.workspace)

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
        lint(textDocument['uri'], self.workspace)

    def m_text_document__did_save(self, textDocument=None, **_kwargs):
        lint(textDocument['uri'], self.workspace)

    def m_text_document__code_action(self, textDocument=None, range=None,
                                     context=None, **_kwargs):
        pass

    def m_text_document__code_lens(self, textDocument=None, **_kwargs):
        return code_lens(textDocument['uri'], self.workspace)

    def m_text_document__completion(self, textDocument=None, position=None,
                                    **_kwargs):
        return completions(textDocument['uri'], self.workspace, position)

    def m_text_document__definition(self, textDocument=None, position=None,
                                    **_kwargs):
        return definitions(textDocument['uri'], self.workspace, position)

    def m_text_document__hover(self, textDocument=None, position=None,
                               **_kwargs):
        return hover()

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
        return find_all_references(textDocument['uri'], self.workspace,
                                   position, context)

    def m_text_document__signature_help(self, textDocument=None, position=None,
                                        **_kwargs):
        pass

    def m_workspace__did_change_configuration(self, settings=None):
        pass

    def m_workspace__did_change_watched_files(self, **_kwargs):
        for change in _kwargs['changes']:
            path = uris.to_fs_path(change['uri'])
            # Grammar changed
            try:
                if os.path.samefile(path,
                                    self.configuration.grammar_path):
                    pass

                # Configuration file changed
                elif os.path.samefile(path,
                                      self.configuration.txconfig_uri):

                    successful = self.configuration.load_configuration()
                    if successful:
                        exts = self.configuration.language_extensions
                        msg = "Configuration changed. Please reopen all files\
                            with \"{}\" extension(s).".format(', '.join(exts))
                        self.workspace.show_message(msg)

                        self.workspace\
                            .remove_by_extension(self.configuration.
                                                 get_all_extensions())

                        self.workspace.parse_all()
                        for doc_uri in self.workspace.documents:
                            lint(doc_uri, self.workspace)
                    else:
                        self.workspace.show_message("Error in .txconfig file.",
                                                    MessageType.Error)
            except:
                pass

            # Other files
            else:
                txdoc = self.workspace.get_document(change['uri'])
                if txdoc is not None:
                    txdoc.parse_model(txdoc.source)
                    lint(change['uri'], self.workspace)

    def m_workspace__execute_command(self, command=None, arguments=None):
        try:
            return self.commands[command](self, arguments)
        except KeyError:
            log.exception("Execute command error.")
            pass
        pass
