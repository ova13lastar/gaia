#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import os
import shutil

import src.gaia.gaia as gaia

FIXTURES_PATH = os.path.normpath(os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), "fixtures"))


def test_gaia_init():
    g = gaia.Gaia(gaia.cfg.get("gaia_src_path"))
    assert isinstance(g, gaia.Gaia)


def test_gaia_init_with_fake_src_path(caplog):
    with pytest.raises(FileNotFoundError):
        gaia.Gaia("fakepath")
    for record in caplog.records:
        assert record.levelname == 'ERROR'
        assert "Chemin absolu du repertoire GAIA introuvable ->" in record.message


########################################


@pytest.fixture(scope='module')
def fakedir_src_path(tmpdir_factory):
    def _init(fakedir=None):
        """ On copie les fixtures desirees : toute l'arborescence si fakedir is None """
        if fakedir is None:
            src_path = tmpdir_factory.mktemp("src_gaia")
        else:
            src_path = tmpdir_factory.mktemp("src_" + fakedir)
        for item in os.listdir(FIXTURES_PATH):
            s = os.path.join(FIXTURES_PATH, item)
            d = os.path.join(src_path, item)
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                except Exception:
                    os.unlink(d)
            if os.path.isdir(s):
                if os.path.basename(s) == fakedir or fakedir is None:
                    shutil.copytree(s, d, symlinks=False, ignore=None)
            else:
                if fakedir is None:
                    shutil.copy2(s, d)
        return src_path
    return _init


########################################


def test_gaia_scan_src_path(fakedir_src_path, caplog):
    """ Test du scan """
    fakesrc_path = fakedir_src_path()
    g = gaia.Gaia(fakesrc_path)
    assert isinstance(g, gaia.Gaia)
    # TODO : assert


@pytest.mark.parametrize('fakedir', ["dir_with_locked_dir"])
def test_gaia_scan_src_path_with_lock_dir(fakedir_src_path, caplog, fakedir):
    """ Test avec un dossier vide """
    fakesrc_path = fakedir_src_path(fakedir)
    # fakedir_path = os.path.join(fakesrc_path, fakedir)
    # Instance de la classe
    g = gaia.Gaia(fakesrc_path)
    g.scan_src_path()
    # Verifications
    for record in caplog.records:
        if record.levelname == 'WARNING':
            assert f"Dossier deja bloque ->" in record.message


# @pytest.mark.parametrize('dirname', ['_archives', '_rejets', '_a'])
# def test_gaia_binding_folders_path(fakedir_src_path, dirname):
#     expected_path = os.path.join((fakedir_src_path()), dirname)
#     g = gaia.Gaia(fakedir_src_path())
#     assert g._init_binding_folders_path(dirname) == expected_path


@pytest.mark.parametrize('fakedir, files_count', [
    ("src_with_1_ini_file", 1),
    ("src_with_2_ini_file", 2),
    ("src_with_multiples_files", 4)])
def test_gaia_check_files_in_src_folder(tmpdir_factory, caplog, fakedir, files_count):
    """ Test avec des fichiers a la racine du src_path """
    fakesrc_path = tmpdir_factory.mktemp("src_gaia")
    for item in os.listdir(FIXTURES_PATH):
        if item == fakedir:
            s = os.path.join(FIXTURES_PATH, item)
            shutil.rmtree(fakesrc_path)
            shutil.copytree(s, fakesrc_path, symlinks=False, ignore=None)
    files = [f for f in os.listdir(fakesrc_path) if os.path.isfile(os.path.join(fakesrc_path, f))]
    # Appel de la methode
    g = gaia.Gaia(fakesrc_path)
    g._check_files_in_src_folder(files)
    # Verifications
    for record in caplog.records:
        if record.levelname == 'WARNING':
            assert f"Des fichiers ont ete detectes dans le repertoire de base -> {files_count}" in record.message


@pytest.mark.parametrize('fakedir, dir_expected, files_expected', [
    ("dir_with_1_subdir", True, False),
    ("dir_with_1_subdir_but_files_in_dir", True, True)])
def test_gaia_check_directories(fakedir_src_path, caplog, fakedir, dir_expected, files_expected):
    """ Test avec des dossiers dans des dossiers du src_path """
    fakesrc_path = fakedir_src_path(fakedir)
    # Appel de la methode
    g = gaia.Gaia(fakesrc_path)
    for curpath, directories, files in os.walk(fakesrc_path):
        # curpath = None
        g._check_directories(directories, files)
    # Verifications
    dir_found = False
    files_found = False
    for record in caplog.records:
        if dir_expected:
            if "directories contient d'autres repertoires" in record.message:
                dir_found = True
        if files_expected:
            if "directories contient aussi des fichiers" in record.message:
                files_found = True
    if dir_expected:
        assert dir_found is True
    if files_expected:
        assert files_found is True


@pytest.mark.parametrize('fakedir', ["dir_empty"])
def test_gaia_scan_src_path_with_dir_empty(fakedir_src_path, fakedir):
    """ Test avec un dossier vide """
    fakesrc_path = fakedir_src_path(fakedir)
    fakedir_path = os.path.join(fakesrc_path, fakedir)
    # Verifications
    dir_contents = os.listdir(fakedir_path)
    assert len(dir_contents) == 0
    # Instance de la classe
    g = gaia.Gaia(fakesrc_path)
    assert isinstance(g, gaia.Gaia)
