import os

from configparser import ConfigParser
from .open_struct import OpenStruct
from .section_struct import SectionStruct

# TODO: use file lock when read/write

def choose_theirs(section, option, mine, theirs):
    return theirs

def choose_mine(section, option, mine, theirs):
    return mine

class ConfigStruct(OpenStruct):
    '''Provides simplified access for managing typed configuration options saved in a file.'''

    def __init__(self, config_file, **sections_defaults):
        super(ConfigStruct, self).__init__()
        self._config_file = config_file
        for (section, items) in sections_defaults.items():
            self[section] = SectionStruct(section, **items)
        self._load(choose_theirs)

    def save(self, conflict_resolver=choose_mine):
        config = self._load(conflict_resolver) # in case some other process has added items
        with open(self._config_file, 'wb') as configfile:
            config.write(configfile)

    ######################################################################
    # private

    def _load(self, conflict_resolver):
        config = ConfigParser()
        if os.path.exists(self._config_file):
            config.read(self._config_file)
        loaded = self._load_theirs(config, conflict_resolver)
        self._load_mine(config, conflict_resolver, loaded)
        return config

    def _load_theirs(self, config, resolver):
        loaded = set()
        for name in config.sections():
            if not self.has_key(name):
                self[name] = SectionStruct(name)
            self[name].sync_with(config, resolver)
            loaded.add(name)
        return loaded

    def _load_mine(self, config, resolver, loaded):
        for (name, section) in self.items():
            if name in loaded:
                continue
            section.sync_with(config, resolver)
