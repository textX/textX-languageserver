# textX language server

**NOTE:** This project is deprecated. It is superseded by [textX-LS](https://github.com/textX/textX-LS).

This is an language server (LS) with [textX](https://github.com/textX/textX) integration written entirely in python.
It implements [Language Server Protocol](https://github.com/Microsoft/language-server-protocol).

## Client Extensions

- [textX-vscode](https://github.com/textX/textX-vscode)

## Project Structure

- `capabilities` (implementation of LS features)
- `commands` (LS commands which includes calling some textX commands)
- `generators` (generating new extensions for our DSLs)
- `infastructure` (implementation of LS core)
- `metamodel` (textX grammars for various DSLs)

## Building and running localy

1. Make sure you have python 3.4+ installed on your machine.
2. Create and activate virtual environment
3. Install server with `pip install textxls`
4. Run server `textxls --tcp`

NOTE:

Steps 4. and 5. are required because new version of textX is not yet published on PyPI.

## Language server features

[![textX language server](http://img.youtube.com/vi/vAP5c7pwWiY/0.jpg)](https://www.youtube.com/watch?v=vAP5c7pwWiY)

Features 3:20 :

1. Linting 3:25
2. Go To Definition 3:35
3. Find All References 3:49
4. Code Completion 4:02
5. Code Outline 3:20
6. Exporting Metamodel dot file 4:11
7. Exporting Model dot file 4:25
8. Soon :)

## Activation events, languages, commands, snippets

Please take a look at [package.json](https://github.com/textX/textX-vscode/blob/master/package.json)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

Some reusable parts of LS core are used from https://github.com/palantir/python-language-server.
