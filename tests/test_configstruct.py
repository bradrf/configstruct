#!/usr/bin/env python

import os
import pytest
import mockfs

from configstruct import ConfigStruct

class TestConfigStruct(object):
    def setup(self):
        self.mfs = mockfs.replace_builtins()
        os.makedirs('/home')

    def teardown(self):
        mockfs.restore_builtins()

    def test_empty_save(self):
        cfg = ConfigStruct('/home/mycfg')
        cfg.save()
        assert os.path.getsize('/home/mycfg') == 0

    def test_repr(self):
        cfg = ConfigStruct('/home/mycfg', options={'stuff': 'nonsense'})
        assert repr(cfg) == '''{'options': {'stuff': 'nonsense'}}'''

    def test_repr_with_overrides(self):
        cfg = ConfigStruct('/home/mycfg', options={'stuff': 'nonsense'})
        cfg.options.might_prefer(fancy=True)
        rc = repr(cfg)
        assert 'nonsense' in rc and 'fancy' in rc

    def test_with_defaults(self):
        cfg = ConfigStruct('/home/mycfg', options={'one': 1})
        assert cfg.options.one == 1
        cfg.save()
        with open('/home/mycfg') as fh:
            assert fh.read().strip() == '[options]\none = 1'

    def test_choose_theirs(self):
        self.mfs.add_entries({'/home/mycfg': '[options]\nfancy = True\n'})
        cfg = ConfigStruct('/home/mycfg', options={'fancy': False})
        assert cfg.options.fancy

    def test_their_added_items(self):
        cfg = ConfigStruct('/home/mycfg', options={})
        self.mfs.add_entries({'/home/mycfg': '[options]\nfancy = True\nshoes = laced'})
        cfg.options.fancy = 'MINE, DAMMIT!'
        cfg.save()
        with open('/home/mycfg') as fh:
            body = fh.read().strip()
            assert 'fancy = MINE, DAMMIT!' in body and 'shoes = laced' in body

    def test_my_added_items(self):
        cfg = ConfigStruct('/home/mycfg', options={})
        self.mfs.add_entries({'/home/mycfg': '[options]\nfancy = True\n'})
        cfg.options.shoes = 'unlaced'
        cfg.save()
        with open('/home/mycfg') as fh:
            body = fh.read().strip()
            assert 'fancy = True' in body and 'shoes = unlaced' in body

    def test_with_overrides(self):
        cfg = ConfigStruct('/home/mycfg', options={'one': 1, 'two': 2})
        cfg.options.might_prefer(one='cage match', two=None)
        assert cfg.options.one == 'cage match' and cfg.options.two == 2

    def test_overrides_are_not_saved(self):
        cfg = ConfigStruct('/home/mycfg', options={'one': 1, 'two': 2})
        cfg.options.might_prefer(one='cage match', two=None)
        cfg.save()
        with open('/home/mycfg') as fh:
            body = fh.read().strip()
            assert 'two = 2' in body and 'one = 1' in body

    def test_set_overrides_are_saved(self):
        cfg = ConfigStruct('/home/mycfg', options={'one': 1, 'two': 2})
        cfg.options.might_prefer(one='cage match', two=None)
        cfg.options.one = 'never mind'
        cfg.save()
        with open('/home/mycfg') as fh:
            body = fh.read().strip()
            assert 'two = 2' in body and 'one = never mind' in body
