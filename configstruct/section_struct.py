from ast import literal_eval
from .open_struct import OpenStruct

class SectionStruct(OpenStruct):
    '''Provides method access to a set of items.'''

    def __init__(self, name, **items):
        self._overrides = {}
        self._name = name
        super(SectionStruct, self).__init__(**items)

    def might_prefer(self, **items):
        '''Items to take precedence if their values are not None (never saved)'''
        self._overrides = dict((k, v) for (k, v) in items.items() if v is not None)

    def sync_with(self, config, conflict_resolver):
        if not config.has_section(self._name):
            config.add_section(self._name)
        resolved = self._resolve_theirs(config, conflict_resolver)
        self._resolve_mine(config, conflict_resolver, resolved)

    ######################################################################
    # private

    def _resolve_theirs(self, config, resolver):
        resolved = set()
        for option, theirs in config.items(self._name):
            theirs = self._real_value_of(theirs)
            if self.has_key(option):
                mine = self[option]
                value = resolver(self._name, option, mine, theirs)
            else:
                value = theirs
            self._set_value(config, option, value)
            resolved.add(option)
        return resolved

    def _resolve_mine(self, config, resolver, resolved):
        for (option, mine) in self.items():
            if option in resolved:
                continue
            if config.has_option(self._name, option):
                theirs = self._real_value_of(config.get(self._name, option))
                value = resolver(self._name, option, mine, theirs)
            else:
                value = mine
            self._set_value(config, option, value)

    def _set_value(self, config, option, value):
        config.set(self._name, option, str(value))
        self[option] = value

    def _real_value_of(self, value):
        try:
            return literal_eval(value)
        except:
            return value

    def __getattr__(self, option):
        if option in self._overrides:
            return self._overrides[option]
        return super(SectionStruct, self).__getattr__(option)

    def __setattr__(self, option, value):
        super(SectionStruct, self).__setattr__(option, value)
        if option in self._overrides:
            # if being explicitly set, the override is no longer applicable
            del(self._overrides[option])

    def __repr__(self):
        if len(self._overrides) > 0:
            rr = super(SectionStruct, self).copy()
            rr.update(self._overrides)
            return repr(rr)
        else:
            return super(SectionStruct, self).__repr__()
