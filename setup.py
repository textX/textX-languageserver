#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

NAME = 'textXlangServer'
DESC = 'Language server for DSLs created with textX'
VERSION = '1.0.0'
AUTHOR = 'Daniel Elero'
AUTHOR_EMAIL = ''
LICENSE = ''
URL = ''
DOWNLOAD_URL = ''
README = ''

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

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
    download_url=DOWNLOAD_URL,
    packages=["..."],
    install_requires=[
        'funcsigs==1.0.2',
        'Jinja2==2.9.6',
        'json-rpc==1.10.3',
        'jsonrpcserver==3.5.1',
        'jsonschema==2.6.0',
        'MarkupSafe==1.0',
        'six==1.11.0',
        'websockets==3.4'
    ],
    dependency_links=[
        '-e git+https://github.com/textX-tools/Arpeggio.git#egg=Arpeggio',
        '-e git+https://github.com/textX-tools/textX.git#egg=textX'
    ],
    keywords="",
    entry_points={
        'console_scripts': [
            'textxls = textx_langserv.__main__:main'
        ]
    }

)
