import os
import sys
import logging

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


LOG_LEVELS = ['debug-all', 'debug', 'info', 'warning', 'error', 'critical']
LOG_OPTIONS = {'log_level': 'info', 'log_file': 'STDERR'}


class OtherLoggingFilter(logging.Filter):
    '''Quell logs from other modules using a different minimum level.'''

    def __init__(self, whitelisted_module, minimum_other_level):
        super(self.__class__, self).__init__(whitelisted_module)
        self._minimum_other_level = minimum_other_level

    def filter(self, record):
        rc = super(self.__class__, self).filter(record)
        if rc != 0:
            return rc  # matched the whitelisted module
        return record.levelno >= self._minimum_other_level


class ConfigStruct(OpenStruct):
    '''Provides simplified access for managing typed configuration options saved in a file.

    :param config_file: path to file that should house configuration items.
    :param log_options_parent: option key to use if this instance is expected to use the
                               `LOG_OPTIONS` default values and allow configuration of basic logging
    :param sections_defaults: options that are provided as defaults (will be overridden by any
           options read from the `config_file`)
    '''

    def __init__(self, config_file, log_options_parent=None, **sections_defaults):
        super(ConfigStruct, self).__init__()
        self._config_file = config_file
        self._log_options_parent = log_options_parent
        if log_options_parent:
            parent_options = sections_defaults.get(log_options_parent, {})
            sections_defaults[log_options_parent] = LOG_OPTIONS.copy()
            sections_defaults[log_options_parent].update(parent_options)
        for (name, items) in sections_defaults.items():
            self[name] = SectionStruct(name, **items)
        self._load(choose_theirs)  # because above were basic defaults for the keys

    def configure_basic_logging(self, main_module_name, **kwargs):
        '''Use common logging options to configure all logging.

        Basic logging configuration is used to set levels for all logs from the main module and to
        filter out logs from other modules unless they are of one level in priority higher.

        :param main_module_name: name of the primary module for normal logging
        '''
        if not self._log_options_parent:
            raise ValueError('Missing log_options_parent')

        options = self[self._log_options_parent]
        log_level_index = LOG_LEVELS.index(options.log_level)
        log_kwargs = {
            'level': getattr(logging, options.log_level.upper()),
            'format': '[%(asctime)s #%(process)d] %(levelname)-8s %(name)-12s %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S%z',
        }

        if options.log_file == 'STDERR':
            log_kwargs['stream'] = sys.stderr
        elif options.log_file == 'STDOUT':
            log_kwargs['stream'] = sys.stdout
        else:
            log_kwargs['filename'] = options.log_file

        log_kwargs.update(kwargs)  # allow overrides from caller
        logging.basicConfig(**log_kwargs)

        # now filter out any other module's logging unless it's one level above the main
        other_log_level = getattr(logging, LOG_LEVELS[log_level_index + 1].upper())
        other_filter = OtherLoggingFilter(main_module_name, other_log_level)
        for handler in logging.root.handlers:
            handler.addFilter(other_filter)

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
