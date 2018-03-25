# Copyright 2017 Palantir Technologies, Inc.
# Added TextXDocument class
import io
import logging
import os
import re
import sys
import itertools

from ..infrastructure import lsp
from ..utils import uris, _utils

from textx.exceptions import TextXSemanticError, TextXSyntaxError

log = logging.getLogger(__name__)

# TODO: this is not the best e.g. we capture numbers
RE_START_WORD = re.compile('[A-Za-z_0-9]*$')
RE_END_WORD = re.compile('^[A-Za-z_0-9]*')


class Workspace(object):

    M_PUBLISH_DIAGNOSTICS = 'textDocument/publishDiagnostics'
    M_APPLY_EDIT = 'workspace/applyEdit'
    M_SHOW_MESSAGE = 'window/showMessage'

    def __init__(self, root_uri, lang_server=None):
        self._root_uri = root_uri
        self._root_uri_scheme = uris.urlparse(self._root_uri)[0]
        self._root_path = uris.to_fs_path(self._root_uri)
        self._docs = {}
        self._lang_server = lang_server

    @property
    def documents(self):
        return self._docs

    @property
    def root_path(self):
        return self._root_path

    @property
    def root_uri(self):
        return self._root_uri

    def is_local(self):
        return (self._root_uri_scheme == '' or
                self._root_uri_scheme == 'file') \
                and os.path.exists(self._root_path)

    def get_document(self, doc_uri):
        try:
            return self._docs[doc_uri]
        except KeyError:
            return None

    def put_document(self, doc_uri, content, version=None):
        document = TextXDocument(
            config=self._lang_server.configuration,
            uri=doc_uri,
            source=content,
            version=version
        )
        self._docs[doc_uri] = document
        return document

    def rm_document(self, doc_uri):
        try:
            self._docs.pop(doc_uri)
        except KeyError:
            pass

    def update_document(self, doc_uri, change, version=None):
        self._docs[doc_uri].apply_change(change)
        self._docs[doc_uri].version = version
        # Parse new model
        self._docs[doc_uri].parse_model(self._docs[doc_uri].source)

    def parse_all(self):
        for doc in self.documents.values():
            doc.parse_model(doc.source)

    def remove_by_extension(self, supported_extensions):
        self._docs = {
            key: val
            for key, val in self.documents.items()
            if val.file_ext in supported_extensions
        }

    def apply_edit(self, edit):
        # Note that lang_server.call currently doesn't return anything
        return self._lang_server.call(self.M_APPLY_EDIT, {'edit': edit})

    def publish_diagnostics(self, doc_uri, diagnostics):
        params = {'uri': doc_uri, 'diagnostics': diagnostics}
        self._lang_server.notify(self.M_PUBLISH_DIAGNOSTICS, params)

    def show_message(self, message, msg_type=lsp.MessageType.Info):
        params = {'type': msg_type, 'message': message}
        self._lang_server.notify(self.M_SHOW_MESSAGE, params)


class Document(object):

    def __init__(self, uri, source=None, version=None, local=True):
        self.uri = uri
        self.version = version
        self.path = uris.to_fs_path(uri)
        self.filename = os.path.basename(self.path)

        self._local = local
        self._source = source

    def __str__(self):
        return str(self.uri)

    @property
    def file_ext(self):
        # If extension is None, return name (e.g. '.txconfig')
        name, ext = os.path.splitext(self.filename)
        return ext or name

    @property
    def lines(self):
        return self.source.splitlines(True)

    @property
    def source(self):
        if self._source is None:
            with open(self.path, 'r') as f:
                return f.read()
        return self._source

    def apply_change(self, change):
        """Apply a change to the document."""
        text = change['text']
        change_range = change.get('range')

        if not change_range:
            # The whole file has changed
            self._source = text
            return

        start_line = change_range['start']['line']
        start_col = change_range['start']['character']
        end_line = change_range['end']['line']
        end_col = change_range['end']['character']

        # Check for an edit occuring at the very end of the file
        if start_line == len(self.lines):
            self._source = self.source + text
            return

        new = io.StringIO()

        # Iterate over the existing document until we hit the edit range,
        # at which point we write the new text, then loop until we hit
        # the end of the range and continue writing.
        for i, line in enumerate(self.lines):
            if i < start_line:
                new.write(line)
                continue

            if i > end_line:
                new.write(line)
                continue

            if i == start_line:
                new.write(line[:start_col])
                new.write(text)

            if i == end_line:
                new.write(line[end_col:])

        self._source = new.getvalue()

    def word_at_position(self, position):
        """
        Get the word under the cursor returning the start and end positions.
        """
        line = self.lines[position['line']]
        i = position['character']
        # Split word in two
        start = line[:i]
        end = line[i:]

        # Take end of start and start of end to find word
        # These are guaranteed to match, even if they match the empty string
        m_start = RE_START_WORD.findall(start)
        m_end = RE_END_WORD.findall(end)

        return m_start[0] + m_end[-1]


class TextXDocument(Document):

    def __init__(self, config, uri, source=None, version=None, local=True):
        super(TextXDocument, self).__init__(uri, source, version, local)

        self.config = config

        self.last_valid_model = None
        self.tx_syntax_errors = []
        self.tx_semantic_errors = []

        self.parse_model(self.source)

    def parse_model(self, model_source, change_state=True):
        """
        Params:
            model_source(string): Textual file representing
                the model.
            change_state(bool): If True, object's state will
                be changed.

        Returns:
            List of syntax errors
            List of semantic errors
        """
        # Return lists
        syn_errs = []
        sem_errs = []

        # Parse
        try:
            log.debug("Parsing model source: " + model_source)
            model = self.config.get_mm_by_ext(self.file_ext)\
                               .model_from_str(model_source)

            # Change object's state
            if change_state:
                log.debug("Parsing model. Model is valid. Source: {0}".format(
                          model_source))
                self.last_valid_model = model

        except TextXSyntaxError as e:
            log.debug("Parsing model syntax error: " + str(e))
            syn_errs.append(e)
        except TextXSemanticError as e:
            log.debug("Parsing model semantic error: " + str(e))
            sem_errs.append(e)

        if change_state:
            self.syntax_errors = syn_errs
            self.semantic_errors = sem_errs

        return syn_errs, sem_errs

    @property
    def is_valid_model(self):
        return len(list(self.all_errors)) == 0

    @property
    def all_errors(self):
        return itertools.chain(self.syntax_errors, self.semantic_errors)

    @property
    def has_syntax_errors(self):
        return len(self.syntax_errors)

    @property
    def has_semantic_errors(self):
        return len(self.semantic_errors)

    def get_rule_inst_at_position(self, position):
        """
        Returns rule at cursor position in model source file
        """
        if self.last_valid_model is None:
            return

        offset = _utils.line_col_to_pos(self.source, position)

        rules_dict = self.last_valid_model._pos_rule_dict

        rule = None
        for p in rules_dict.keys():
            if p[1] > offset > p[0]:
                rule = rules_dict[p]
                break

        return rule

    def get_all_rule_instances(self):
        """
        Concatenate builtins with rule list
        """
        builtins = []
        try:
            builtins = list(self.config.get_mm_by_ext(
                                self.file_ext).builtins.values())
        except:
            pass

        from_model = list(self.last_valid_model._pos_rule_dict.values())
        all_rules = from_model + builtins
        log.debug("Get all rules: " + ','.join(str(r) for r in all_rules))
        return all_rules
