#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
from setuptools import setup, find_packages

NAME = 'textXLanguageServer'
DESC = 'Language server for DSLs created with textX'
VERSION = '1.0.0'
AUTHOR = 'Daniel Elero'
AUTHOR_EMAIL = 'danixeee AT gmail DOT com'
LICENSE = 'MIT'
URL = 'https://github.com/textX-tools/textX-languageserver'
README = ''
# README = codecs.open(os.path.join(os.path.dirname(__file__), 'README.rst'),
#                      'r', encoding='utf-8').read()

setup(
    name=NAME,
    version=VERSION,
    description=DESC,
    long_description=README,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    packages=find_packages(),
    package_data={'textx_langserv.metamodel': ['*tx']},
    install_requires=[
        'funcsigs==1.0.2',
        'Jinja2==2.9.6',
        'json-rpc==1.10.3',
        'jsonrpcserver==3.5.1',
        'jsonschema==2.6.0',
        'MarkupSafe==1.0',
        'six==1.11.0',
        'websockets==3.4',
        'Arpeggio==1.7',
        'textX'
    ],
    dependency_links=[
        'https://github.com/textX-tools/textX/tarball/pull_request#egg=textX'
    ],
    keywords="textx vscode extension",
    entry_points={
        'console_scripts': [
            'textxls = textx_langserv.__main__:main'
        ]
    }

)
