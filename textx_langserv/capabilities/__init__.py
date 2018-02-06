from textx_langserv.infrastructure import lsp


def get_capabilities():
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
                'commands': ['genext', 'outline.refresh']
            },
            'hoverProvider': True,
            'referencesProvider': True,
            'signatureHelpProvider': {
                'triggerCharacters': ['(', ',']
            },
            'textDocumentSync': lsp.TextDocumentSyncKind.INCREMENTAL
    }
