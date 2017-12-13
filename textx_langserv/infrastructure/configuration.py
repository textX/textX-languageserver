import os

from functools import partial
from os.path import join, dirname

from textx.metamodel import metamodel_from_file

from utils import uris
from utils._utils import flatten
from utils.constants import TX_TX_EXTENSION, TX_CONFIG_EXTENSION, \
TX_OUTLINE_EXTENSION, TX_COLORING_EXTENSION


this_folder = dirname(__file__)


class Configuration(object):

    def __init__(self, root_uri):
        self.root_uri = root_uri
        self.txconfig_uri = join(uris.to_fs_path(root_uri), TX_CONFIG_EXTENSION)
        self.config_model = None

        self._loader = lambda path, classes=[], builtins={}: \
                        metamodel_from_file(join(this_folder,'../metamodel', path),
                                            classes=classes,
                                            builtins=builtins)

        self.dsls_info = [
            (['.tx'],       partial(self._loader,'textx.tx')),
            (['.txconfig'], partial(self._loader,'configuration.tx')),
            (['.txcl'],     partial(self._loader,'coloring.tx')),
            (['.txol'],     partial(self._loader,'outline.tx'))
        ]

        self.load_configuration()


    def _get_mm_loader_by_ext(self, ext):
        for dsl_exts, mm_loader in self.dsls_info:
            if ext in dsl_exts:
                return mm_loader


    def get_mm_by_ext(self, ext):
        return self._get_mm_loader_by_ext(ext)()

    
    def load_configuration(self):
        try:
            self.config_model = self.get_mm_by_ext(TX_CONFIG_EXTENSION) \
                                    .model_from_file(self.txconfig_uri)
            self.load_metamodel()
        except:
            return False

        return True
    

    def load_metamodel(self):
        def get_func_from_module_path(path, module_name):
            import imp
            func_name = path[2:].split(':')[1]
            path_name = path.replace(':{}'.format(func_name),'')
            module = imp.load_source(module_name, path_name)
            return getattr(module, func_name)

        classes = get_func_from_module_path(self.mm_classes, "_custom_classes")()
        builtins = get_func_from_module_path(self.mm_builtins, "_custom_builtins")()

        self.dsls_info.append((self.language_extensions, partial(self._loader,
                                                                self.grammar_path,
                                                                classes,
                                                                builtins)))

 
    def get_all_extensions(self):
        return flatten([ext for ext, _ in self.dsls_info])   


    @property
    def language_name(self):
        return self.config_model.name

    @property
    def language_extensions(self):
        return ['.'+ ext for ext in self.config_model.extensions]

    @property
    def publisher(self):
        return self.getValue('general', 'publisher')

    @property
    def url(self):
        return self.getValue('general', 'url')

    @property
    def author(self):
        return self.getValue('general', 'author')

    @property
    def version(self):
        return self.getValue('general', 'version')

    @property
    def grammar_path(self):
        return self.getValue('path', 'grammar')

    @property
    def coloring_path(self):
        return self.getValue('path', 'coloring')

    @property
    def outline_model(self):
        outline_mm = self.get_mm_by_ext(TX_OUTLINE_EXTENSION)
        path = self.getValue('path', 'outline')
        return outline_mm.model_from_file(join(uris.to_fs_path(self.root_uri), path))

    @property
    def genereting_path(self):
        return self.getValue('path', 'generating')

    @property
    def project_path(self):
        return join(self.genereting_path, self.language_name)

    @property
    def mm_classes(self):
        return self.getValue('path', 'classes')

    @property
    def mm_builtins(self):
        return self.getValue('path', 'builtins')

    def getValue(self, rule, option):
        ret_val = None
        for rule_item in self.config_model.rules:
            if rule_item.name == rule:
                for option_item in rule_item.options:
                    if option_item.name == option:
                        ret_val = option_item.value
        if ret_val and rule == 'path':
            return to_fs_path(self.root_uri, ret_val)

        return ret_val


def to_fs_path(root_uri, path):
    """
    Handle relative and absolute paths
    """
    is_abs = os.path.isabs(path)
    if is_abs:
        return path
    else:
        return join(uris.to_fs_path(root_uri), path)