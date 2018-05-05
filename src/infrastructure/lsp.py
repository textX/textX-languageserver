"""Some Language Server Protocol constants

https://github.com/Microsoft/language-server-protocol/blob/master/protocol.md
"""


class CompletionItemKind(object):
    Text = 1
    Method = 2
    Function = 3
    Constructor = 4
    Field = 5
    Variable = 6
    Class = 7
    Interface = 8
    Module = 9
    Property = 10
    Unit = 11
    Value = 12
    Enum = 13
    Keyword = 14
    Snippet = 15
    Color = 16
    File = 17
    Reference = 18


class DiagnosticSeverity(object):
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4


class MessageType(object):
    Error = 1
    Warning = 2
    Info = 3
    Log = 4


class SymbolKind(object):
    File = 1
    Module = 2
    Namespace = 3
    Package = 4
    Class = 5
    Method = 6
    Property = 7
    Field = 8
    Constructor = 9
    Enum = 10
    Interface = 11
    Function = 12
    Variable = 13
    Constant = 14
    String = 15
    Number = 16
    Boolean = 17
    Array = 18


class TextDocumentSyncKind(object):
    NONE = 0
    FULL = 1
    INCREMENTAL = 2


class Diagnostic(object):

    def __init__(self):
        self.diagnostics = []

    def error(self, lines, line, col, message,
              severity=None, code=None, source=None):
        line = line or 1
        col = col or 1
        range = {
            'start': {'line': line-1, 'col': col},
            'end': {'line': line-1, 'col': col+len(lines[line-1])}
        }
        self.diagnostics.append({
            'range': range,
            'message': message,
            'source': source,
            'code': code,
            'severity': DiagnosticSeverity.Error
        })

    def get_diagnostics(self):
        return self.diagnostics


class Completions(object):

    def __init__(self):
        self.completions = []

    def add_completion(self, label,
                       kind=CompletionItemKind.Keyword,
                       insert_text_format=1,
                       insert_text=None,
                       sort=None,
                       detail=None,
                       documentation=None):
        self.completions.append({
            'label': label,
            'kind': kind,
            'sortText': len(self.completions),
            'insertTextFormat': insert_text_format,
            'insertText': insert_text
        })

    def get_completions(self):
        return self.completions
