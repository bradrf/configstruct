import os

from configparser import ConfigParser
from .open_struct import OpenStruct
from .section_struct import SectionStruct

# TODO: use file lock when read/write


def choose_theirs(section, option, mine, theirs):
    '''Always prefer values for keys from file.'''
    return theirs


def choose_mine(section, option, mine, theirs):
    '''Always prefer values for keys in memory.'''
    return mine


class ConfigStruct(OpenStruct):
    '''Provides simplified access for managing typed configuration options saved in a file.

    :param config_file: path to file that should house configuration items.
    :param sections_defaults: options that should provide as defaults (will be overridden by any
           options read from the `config_file`)
    '''

    def __init__(self, config_file, **sections_defaults):
        super(ConfigStruct, self).__init__()
        self._config_file = config_file
        for (name, items) in sections_defaults.items():
            self[name] = SectionStruct(name, **items)
        self._load(choose_theirs)  # because above were basic defaults for the keys

    def save(self, conflict_resolver=choose_mine):
        '''Save all options in memory to the `config_file`.

        Options are read once more from the file (to allow other writers to save configuration),
        keys in conflict are resolved, and the final results are written back to the file.

        :param conflict_resolver: a simple lambda or function to choose when an option key is
               provided from an outside source (THEIRS, usually a file on disk) but is also already
               set on this ConfigStruct (MINE)
        '''
        config = self._load(conflict_resolver)  # in case some other process has added items
        with open(self._config_file, 'wb') as cf:
            config.write(cf)

    ######################################################################
    # private

    def _load(self, resolver):
        config = ConfigParser()
        if os.path.exists(self._config_file):
            with open(self._config_file) as cf:
                config.readfp(cf)  # use readfp as read somehow circumvents mockfs in tests
        loaded = self._sync_sections_with(config, resolver)
        self._add_new_sections(config, loaded)
        return config

    def _sync_sections_with(self, config, resolver):
        loaded = set()
        for name in config.sections():
            if name not in self:
                self[name] = SectionStruct(name)
            self[name].sync_with(config, resolver)
            loaded.add(name)
        return loaded

    def _add_new_sections(self, config, seen):
        for name in self:
            if name not in seen:
                self[name].sync_with(config, choose_mine)  # new ones, so always "mine"
