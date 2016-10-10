class OpenStruct(dict):
    '''Base wrapper to allow direct method access to item keys.'''

    ######################################################################
    # private

    def __getattr__(self, key):
        if key[0] == '_':
            return self.__dict__[key]
        else:
            return self.get(key)

    def __setattr__(self, key, value):
        if key[0] == '_':
            self.__dict__[key] = value
        else:
            self[key] = value

    def __hasattr__(self, key):
        return self.has_key(key)

    def __delattr__(self, key):
        if self.has_key(key):
            del(self[key])
