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
        '''Synchronizes current set of key/values in this instance with those in the config.'''
        if not config.has_section(self._name):
            config.add_section(self._name)
        resolved = self._sync_and_resolve(config, conflict_resolver)
        self._add_new_items(config, resolved)

    ######################################################################
    # private

    def _sync_and_resolve(self, config, resolver):
        '''Synchronize all items represented by the config according to the resolver and return a
        set of keys that have been resolved.'''
        resolved = set()
        for key, theirs in config.items(self._name):
            theirs = self._real_value_of(theirs)
            if key in self:
                mine = self[key]
                value = resolver(self._name, key, mine, theirs)
            else:
                value = theirs
            self._set_value(config, key, value)
            resolved.add(key)
        return resolved

    def _add_new_items(self, config, seen):
        '''Add new (unseen) items to the config.'''
        for (key, value) in self.items():
            if key not in seen:
                self._set_value(config, key, value)

    def _set_value(self, config, key, value):
        config.set(self._name, key, str(value))
        self[key] = value

    def _real_value_of(self, value):
        try:
            return literal_eval(value)
        except:
            return value

    def __getattr__(self, key):
        if key in self._overrides:
            return self._overrides[key]
        return super(SectionStruct, self).__getattr__(key)

    def __setattr__(self, key, value):
        super(SectionStruct, self).__setattr__(key, value)
        if key in self._overrides:
            # if being explicitly set, the override is no longer applicable
            del(self._overrides[key])

    def __repr__(self):
        if len(self._overrides) > 0:
            rr = super(SectionStruct, self).copy()
            rr.update(self._overrides)
            return repr(rr)
        else:
            return super(SectionStruct, self).__repr__()
