#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
from setuptools import setup, find_packages

NAME = 'textXls'
DESC = 'Language server for DSLs created with textX'
VERSION = '1.1.0'
AUTHOR = 'Daniel Elero'
AUTHOR_EMAIL = 'danixeee@gmail.com'
LICENSE = 'MIT'
URL = 'https://github.com/textX-tools/textX-languageserver'
README = codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'),
                     'r', encoding='utf-8').read()

setup(
    name=NAME,
    version=VERSION,
    description=DESC,
    long_description=README,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=URL,
    packages=find_packages(),
    package_data={'src.metamodel': ['*tx']},
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
        'git+https://github.com/igordejanovic/textX.git@master#egg=textX'
    ],
    keywords="textx language server protocol LSP DSL",
    entry_points={
        'console_scripts': [
            'textxls = src.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
    ]
)
