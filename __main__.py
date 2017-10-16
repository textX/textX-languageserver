import argparse
import json
import sys
import os

import language_server
from textx_ls import TextXLanguageServer


def main():
    host = "127.0.0.1"
    port = 5000
    print("STARTING: {0}:{1}".format(host,port))
    language_server.start_tcp_lang_server(host, port, TextXLanguageServer)

if __name__ == "__main__":
    main()
