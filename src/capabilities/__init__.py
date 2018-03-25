from ..infrastructure import lsp


def get_capabilities(cmd_list):
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
                'commands': cmd_list
            },
            'hoverProvider': True,
            'referencesProvider': True,
            'signatureHelpProvider': {
                'triggerCharacters': ['(', ',']
            },
            'textDocumentSync': lsp.TextDocumentSyncKind.INCREMENTAL
    }
