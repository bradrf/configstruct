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

    def test_with_defaults(self):
        cfg = ConfigStruct('/home/mycfg', options={'one': 1, 'two': 2})
        assert cfg.options.two == 2
        cfg.save()
        with open('/home/mycfg') as fh:
            assert fh.read().strip() == '[options]\ntwo = 2\none = 1'

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
            assert fh.read().strip() == '[options]\nfancy = MINE, DAMMIT!\nshoes = laced'
