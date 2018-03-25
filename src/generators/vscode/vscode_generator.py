"""
This module is responsible for creating
VS Code extension with Language Server
based on config file and other DSLs for
code outline, syntax highlighting, ...
"""
import os
import re
import tempfile
import errno
import fileinput
from os.path import join, dirname

from distutils.dir_util import copy_tree
from shutil import copy2
from jinja2 import Environment, FileSystemLoader

from ...utils.uris import to_fs_path

from ... import EXTENSION_ROOT_PATH
from ...utils.constants import SERVER_TCP

from ...generators.vscode.coloring import ColoringVSCode

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

        make_gen_dirs(gen_path)

        # Copy extension
        copy_tree(EXTENSION_ROOT_PATH, gen_path)

        # Copy .txconfig
        gen_config_path = join(gen_path,
                               'textX-languageserver/src/txconfig')
        cfg = copy_configs(textx_ls.configuration, gen_config_path, env)

        # Copy outline icons
        new_outline_path = cfg['outline_path']
        copy_outline(gen_config_path, textx_ls, new_outline_path)

        # Replace other files
        generate_package_json(gen_path, textx_ls, env)
        generate_server_config_json(gen_path, env)
        generate_tm_coloring_json(gen_path, textx_ls, env)

        msg = "Generating completed > {}".format(gen_path)
        textx_ls.workspace.show_message(msg)

    except:
        msg = "Generating failed."
        textx_ls.workspace.show_message(msg)
    finally:
        textx_ls.gen_cmd_finished = True


def make_gen_dirs(gen_path):
    path = join(gen_path,
                'textX-languageserver/src/txconfig/icons')

    if not os.path.exists(path):
        os.makedirs(path)


def copy_configs(config, gen_config_path, env):
    # Copy grammar
    grammar_path = copy2(config.grammar_path, gen_config_path)
    # Copy outline
    outline_path = ''
    coloring_path = ''
    classes_path = ''
    builtins_path = ''

    try:
        outline_path = copy2(config.outline_path, gen_config_path)
    except:
        pass
    # Copy coloring
    try:
        coloring_path = copy2(config.coloring_path, gen_config_path)
    except:
        pass
    # Copy classes
    try:
        classes_parts = config.classes_path.split(':')
        classes_path = copy2(classes_parts[0], gen_config_path)
        classes_path = '{}:{}'.format(classes_path, classes_parts[1])
    except:
        pass
    # Copy builtins
    try:
        builtins_parts = config.builtins_path.split(':')
        builtins_path = copy2(builtins_parts[0], gen_config_path)
        builtins_path = '{}:{}'.format(builtins_path, builtins_parts[1])
        builtins_path = copy2(config.builtins_path, gen_config_path)
    except:
        pass

    cfg = {
        'name': config.language_name,
        'extensions': config.config_model.extensions,
        'publisher': config.publisher,
        'url': config.repo_url,
        'version': config.version,
        'grammar_path': grammar_path,
        'outline_path': outline_path,
        'coloring_path': coloring_path,
        'classes_path': classes_path,
        'builtins_path': builtins_path
    }

    # Add new .txconfig
    template = env.get_template('txconfig.template')
    with open(join(gen_config_path, '.txconfig'), 'w') as f:
        f.write(template.render(cfg))

    return cfg


def copy_outline(gen_config_path, textx_ls, new_outline_path):
    # Copy outline icons
    config = textx_ls.configuration
    outline_path_dir = dirname(config.outline_path)
    icon_paths = _get_outline_icon_paths(config.outline_model)
    dest = join(gen_config_path, 'icons')

    path_map = {}
    for path in icon_paths:
        icon_abs_path = join(outline_path_dir, path)
        new_path = copy2(icon_abs_path, dest)
        try:
            path_map[path] = new_path
        except:
            pass

    with fileinput.FileInput(new_outline_path, inplace=True) as file:
        pattern = r'".*"'
        for line in file:
            m = re.search(pattern, line)
            if m is not None:
                p = m.group().replace('"', '').replace("'", '')
                print(line.replace(p, path_map[p]), end='')
            else:
                print(line, end='')


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
    coloring = ColoringVSCode(textx_ls.configuration)
    with open(join(gen_path, 'syntaxes', coloring_file_name), 'w') as f:
        f.write(template.render(coloring.get_coloring_model()))


def _get_outline_icon_paths(outline_model):
    paths = []
    for rule in outline_model.rules:
        if rule.icon:
            paths.append(rule.icon.path)
    return paths


def validate_config_file(textx_ls):
    errors = []
    cfg = textx_ls.configuration

    if not cfg.version:
        errors.append("Version is required.")
    if not cfg.publisher:
        errors.append("Publisher is required.")

    return errors
