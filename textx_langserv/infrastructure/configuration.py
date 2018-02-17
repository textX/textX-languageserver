"""
Module for reading configuration file
"""
import os

from functools import partial
from os.path import join, dirname

from textx.metamodel import metamodel_from_file

from textx_langserv.utils import uris
from textx_langserv.utils._utils import flatten
from textx_langserv.utils.constants import TX_TX_EXTENSION,\
    TX_CONFIG_EXTENSION, TX_OUTLINE_EXTENSION, TX_COLORING_EXTENSION, \
    TX_METAMODEL, CONFIG_METAMODEL, COLORING_METAMODEL, OUTLINE_METAMODEL

from textx_langserv import LS_ROOT_PATH

__author__ = "Daniel Elero"
__copyright__ = "textX-tools"
__license__ = "MIT"


class Configuration(object):

    def __init__(self, root_uri):
        self.root_uri = root_uri
        self.txconfig_uri = join(uris.to_fs_path(root_uri),
                                 TX_CONFIG_EXTENSION)
        self.config_model = None

        self._loader = lambda path, classes=[], builtins={}: \
            metamodel_from_file(join(LS_ROOT_PATH,
                                     'metamodel',
                                     path),
                                textx_tools_support=True,
                                classes=classes,
                                builtins=builtins)

        self.languages = [
            ([TX_TX_EXTENSION], partial(self._loader, 'textx.tx')),
            ([TX_CONFIG_EXTENSION], partial(self._loader, 'configuration.tx')),
            ([TX_COLORING_EXTENSION], partial(self._loader, 'coloring.tx')),
            ([TX_OUTLINE_EXTENSION], partial(self._loader, 'outline.tx'))
        ]
        self.builtin_lang_len = len(self.languages)

        self.load_configuration()

    def load_configuration(self):
        try:
            self.config_model = self.get_mm_by_ext(TX_CONFIG_EXTENSION) \
                                    .model_from_file(self.txconfig_uri)
            self.load_metamodel()
            return True
        except:
            return False

    def _get_mm_loader_by_ext(self, ext):
        for dsl_exts, mm_loader in self.languages:
            if ext in dsl_exts:
                return mm_loader

    def get_mm_by_ext(self, ext):
        return self._get_mm_loader_by_ext(ext)()

    def load_metamodel(self):
        def exec_func_from_module_path(path, module_name):
            import imp
            try:
                func_name = path[2:].split(':')[1]
                path_name = path.replace(':{}'.format(func_name), '')
                module = imp.load_source(module_name, path_name)
                return getattr(module, func_name)()
            except:
                return None

        classes = exec_func_from_module_path(self.classes_path,
                                             "_custom_classes")
        builtins = exec_func_from_module_path(self.builtins_path,
                                              "_custom_builtins")

        self.reset_languages_list()
        self.languages.append((self.language_extensions,
                               partial(self._loader,
                                       self.grammar_path,
                                       classes,
                                       builtins)))

    def reset_languages_list(self):
        if len(self.languages) > self.builtin_lang_len:
            self.languages.pop()

    def get_all_extensions(self):
        return flatten([ext for ext, _ in self.languages])

    @property
    def language_name(self):
        return self.config_model.name

    @property
    def language_extensions(self):
        return ['.' + ext for ext in self.config_model.extensions]

    @property
    def publisher(self):
        return self.config_model.general_section.publisher

    @property
    def url(self):
        return self.config_model.general_section.url

    @property
    def author(self):
        return self.config_model.general_section.author

    @property
    def version(self):
        return self.config_model.general_section.version

    @property
    def grammar_path(self):
        path = self.config_model.paths_section.grammar_path
        return to_fs_path(self.root_uri, path)

    @property
    def coloring_path(self):
        path = self.config_model.paths_section.coloring_path
        return to_fs_path(self.root_uri, path)

    @property
    def outline_path(self):
        path = self.config_model.paths_section.outline_path
        return to_fs_path(self.root_uri, path)

    @property
    def classes_path(self):
        path = self.config_model.paths_section.classes_path
        return to_fs_path(self.root_uri, path)

    @property
    def builtins_path(self):
        path = self.config_model.paths_section.builtins_path
        return to_fs_path(self.root_uri, path)

    @property
    def outline_model(self):
        outline_mm = self.get_mm_by_ext(TX_OUTLINE_EXTENSION)
        path = self.outline_path
        return outline_mm.model_from_file(
            join(uris.to_fs_path(self.root_uri), path))


def to_fs_path(root_uri, path):
    """
    Handle relative and absolute paths
    """
    if path.isspace():
        return None

    is_abs = os.path.isabs(path)
    if is_abs:
        return path
    else:
        return join(uris.to_fs_path(root_uri), path)
