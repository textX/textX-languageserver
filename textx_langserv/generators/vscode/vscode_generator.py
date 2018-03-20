"""
This module is responsible for creating
VS Code extension with Language Server
based on config file and other DSLs for
code outline, syntax highlighting, ...
"""
import os
import tempfile
from os.path import join, dirname

from distutils.dir_util import copy_tree
from jinja2 import Environment, FileSystemLoader

from textx_langserv.utils.uris import to_fs_path

from textx_langserv import EXTENSION_ROOT_PATH
from textx_langserv.utils.constants import SERVER_TCP

from textx_langserv.generators.vscode.coloring import get_coloring_model

this_folder = dirname(__file__)


def generate(textx_ls, args):
    try:
        gen_path = join(to_fs_path(textx_ls.root_uri), 'gen')
        if '.vscode' not in this_folder:
            return

        errors = validate_config_file(textx_ls)
        if errors:
            msg = "Missing fields in .txconfig file.\n{}"\
                  .format('\n'.join(errors))
            textx_ls.workspace.show_message(msg)
            return

        textx_ls.gen_cmd_finished = False
        msg = "Generating extension."
        textx_ls.workspace.show_message(msg)

        env = Environment(loader=FileSystemLoader(join(this_folder,
                                                  'templates')),
                          trim_blocks=True,
                          lstrip_blocks=True)

        if not os.path.exists(gen_path):
            os.makedirs(gen_path)

        copy_tree(EXTENSION_ROOT_PATH, gen_path)
        generate_package_json(gen_path, textx_ls, env)
        generate_server_config_json(gen_path, env)
        generate_tm_coloring_json(gen_path, textx_ls, env)

        msg = "Generating completed > {}".format(gen_path)
        textx_ls.workspace.show_message(msg)

    except:
        pass
    finally:
        textx_ls.gen_cmd_finished = True


def generate_package_json(gen_path, textx_ls, env):
    template = env.get_template('package_json.template')
    with open(join(gen_path, 'package.json'), 'w') as f:
        f.write(template.render(config=textx_ls.configuration))


def generate_server_config_json(gen_path, env):
    template = env.get_template('serverconfig_json.template')
    with open(join(gen_path, 'server_config.json'), 'w') as f:
        f.write(template.render())


def generate_tm_coloring_json(gen_path, textx_ls, env):
    template = env.get_template('coloring_json.template')
    lang_name = textx_ls.configuration.language_name
    coloring_file_name = lang_name.lower() + '.tmLanguage.json'
    with open(join(gen_path, 'syntaxes', coloring_file_name), 'w') as f:
        f.write(template.render(test=get_coloring_model(textx_ls)))


def validate_config_file(textx_ls):
    errors = []
    cfg = textx_ls.configuration

    if not cfg.version:
        errors.append("Version is required.")
    if not cfg.publisher:
        errors.append("Publisher is required.")

    return errors
