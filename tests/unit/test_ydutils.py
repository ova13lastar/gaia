#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import os

import src.gaia.ydutils as ydutils

FIXTURES_PATH = os.path.normpath(os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), "fixtures"))


@pytest.mark.parametrize('v, expected', [('1', True), (1, True), ('a', False), ('1.2', False), (1.2, False)])
def test_isint(v, expected):
    assert ydutils.isint(v) == expected


@pytest.mark.parametrize('v, expected', [('1.2', True), (1.2, True), ('a', False), ('1', False), (1, False)])
def test_isfloat(v, expected):
    assert ydutils.isfloat(v) == expected


@pytest.mark.parametrize('v, expected', [('181044700105823', True), ('181044700105899', False),
                                         ('a', False), ('1810447001058', False)])
def test_isvalid_nir(v, expected):
    assert ydutils.isvalid_nir(v) == expected


@pytest.mark.parametrize('v, expected', [
    (0, '0B'), (100, '100.0 B'), (1000, '1000.0 B'), (10000, '9.77 KB'), (100000, '97.66 KB'),
    (1000000, '976.56 KB'), (10000000, '9.54 MB'), (100000000, '95.37 MB'), (1000000000, '953.67 MB'),
    (10000000000, '9.31 GB'), (100000000000, '93.13 GB'), (1000000000000, '931.32 GB'), (10000000000000, '9.09 TB')])
def test_convert_filesize(v, expected):
    assert ydutils.convert_filesize(v) == expected


@pytest.mark.parametrize('v, expected', [
    (os.path.join(FIXTURES_PATH, *["dir_with_locked_dir", "dir_locked.lock"]), True),
    (os.path.join(FIXTURES_PATH, *["dir_with_locked_dir", "dir_not_locked"]), False)])
def test_is_locked_dir(v, expected, caplog):
    assert ydutils.is_locked_dir(v) == expected
