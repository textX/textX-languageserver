from textx.metamodel import metamodel_from_file

from utils import constants, uris
from utils._utils import flatten

from os.path import join, dirname

import glob

this_folder = dirname(__file__)



class Configuration(object):

    def __init__(self, root_uri):
        tx_mm = metamodel_from_file(join(this_folder,'../metamodel/textx.tx'))
        tx_config_mm = metamodel_from_file(join(this_folder,'../metamodel/configuration.tx'))
        tx_coloring_mm = metamodel_from_file(join(this_folder,'../metamodel/coloring.tx'))
        
        self.config_model = tx_config_mm.model_from_file(join(uris.to_fs_path(root_uri),'.txconfig'))

        self.dsls = {
            '_tx_txlang': (['.tx'], tx_mm),
            '_tx_configlang': (['.txconfig'], tx_config_mm),
            '_tx_coloringlang': (['.clr'], tx_coloring_mm),
            self.language_name: (self.language_extensions, metamodel_from_file(self.grammar_path))
        }


    def get_metamodel_by_dsl_name(self, dsl_name):
        try:
            _, mm = self.dsls[dsl_name]
            return mm
        except:
            return None


    def get_metamodel_by_dsl_ext(self, dsl_ext):
        for dsl in self.dsls.values():
            exts, mm = dsl
            if dsl_ext in exts:
                return mm


    def get_all_extensions(self):
        return flatten([ext for ext, _ in self.dsls.values()])
        

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
    def outline_path(self):
        return self.getValue('path', 'outline')

    @property
    def genereting_path(self):
        return self.getValue('path', 'generating')

    @property
    def project_path(self):
        return join(self.genereting_path, self.language_name)

    @property
    def python_interpreter(self):
        return self.getValue('python', 'interpreter')

    def getValue(self, rule, option):
        for rule_item in self.config_model.rules:
            if rule_item.name == rule:
                for option_item in rule_item.options:
                    if option_item.name == option:
                        return option_item.value
        return None