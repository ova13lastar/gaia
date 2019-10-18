#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import logging
import configparser

import src.gaia.config as config


@pytest.fixture(scope='module')
def fakedir_conf_path(tmpdir_factory):
    return tmpdir_factory.mktemp("fakedir_conf")


@pytest.fixture(scope='module')
def fakefile_appconf_path(fakedir_conf_path):
    fakefile_appconf_path = fakedir_conf_path.join("fakefile." + config.CONF_FILEEXT)
    with open(fakefile_appconf_path, 'w') as f:
        f.write('[DEFAULT]\n')
        f.write('log_level = DEBUG\n')
        f.write('str1 = value1\n')
        f.write('str2=value2\n')
        f.write('str3 : value3\n')
        f.write('str4:value4\n')
        f.write('int1 = 1\n')
        f.write('int2 = 1.2\n')
        f.write('bool1 = True\n')
        f.write('bool2 = False\n')
    return fakefile_appconf_path


@pytest.fixture(scope='module')
def fakefile_logconf_path(fakedir_conf_path):
    fakefile_logconf_path = fakedir_conf_path.join("fakefile." + config.CONF_FILEEXT)
    with open(fakefile_logconf_path, 'w') as f:
        f.write('[loggers]\n')
        f.write('keys=root\n')
        f.write('[handlers]\n')
        f.write('keys=consoleHandler\n')
        f.write('[formatters]\n')
        f.write('keys=MainFormatter\n')
        f.write('[formatter_MainFormatter]\n')
        f.write('[handler_consoleHandler]\n')
        f.write('class=StreamHandler\n')
        f.write('level=DEBUG\n')
        f.write('formatter=MainFormatter\n')
        f.write('args=(sys.stdout,)\n')
        f.write('[logger_root]\n')
        f.write('level=DEBUG\n')
        f.write('handlers=consoleHandler\n')
    return fakefile_logconf_path


########################################


def test_log(caplog):
    """ Test nominal """
    caplog.set_level(logging.INFO)
    logconfig = config.LogConfig(config.LOG_INIFILE_PATH)
    assert isinstance(logconfig, config.LogConfig)
    for record in caplog.records:
        assert record.levelname == 'INFO'
        assert "DEMARRAGE DE L'APPLICATION" in record.message


def test_log_is_singleton():
    """ Test singleton """
    logconfig1 = config.LogConfig(config.LOG_INIFILE_PATH)
    logconfig2 = config.LogConfig(config.LOG_INIFILE_PATH)
    assert logconfig1 == logconfig2


def test_log_init_with_empty_ini_file(caplog):
    """ Test avec fichier de config vide """
    with pytest.raises(FileNotFoundError):
        config.LogConfig("")
    for record in caplog.records:
        assert record.levelname == 'CRITICAL'
        assert "Fichier de configuration du logger introuvable ->" in record.message


def test_log_init_with_exception(fakedir_conf_path, caplog):
    """ Test avec fichier de config avec valeur erronee """
    fakefile_logcfg_path = fakedir_conf_path.join("fakefile." + config.CONF_FILEEXT)
    with open(fakefile_logcfg_path, 'w') as f:
        f.write('fakedata')
    with pytest.raises(SystemExit):
        config.LogConfig(fakefile_logcfg_path)
    for record in caplog.records:
        assert record.levelname == 'CRITICAL'
        assert "Impossible d'initialiser le logger" in record.message


def test_log_init_with_fake_inifile(fakefile_logconf_path):
    """ Test avec fichier de config valide rempli avec des fakes """
    logconfig = config.LogConfig(fakefile_logconf_path)
    assert isinstance(logconfig, config.LogConfig)

# def test_log_get_logger_with_warning_log_level(fakedir_conf_path):
#     """ Test du logger avec fichier de config contenant un niveau de log WARNING """
#     fakefile_appcfg_path = fakedir_conf_path.join("fakefile." + config.CONF_FILEEXT)
#     fakeloglevel = "WARNING"
#     with open(fakefile_appcfg_path, 'w') as f:
#         f.write('[DEFAULT]\n')
#         f.write(f'log_level = {fakeloglevel}\n')
#     cfg = config.AppConfig(fakefile_appcfg_path)
#     logconfig = config.LogConfig(config.LOG_INIFILE_PATH)
#     log = logconfig.get_logger(cfg)
#     assert log.getEffectiveLevel() == logging.getLevelName(fakeloglevel)


########################################


def test_config(caplog):
    """ Test nominal """
    caplog.set_level(logging.INFO)
    cfg = config.AppConfig(config.APP_INIFILE_PATH)
    assert isinstance(cfg, config.AppConfig)
    for record in caplog.records:
        assert record.levelname == 'INFO'
        assert "Niveau de log ->" in record.message


def test_config_is_singleton():
    """ Test singleton """
    cfg1 = config.AppConfig(config.APP_INIFILE_PATH)
    cfg2 = config.AppConfig(config.APP_INIFILE_PATH)
    assert cfg1 == cfg2


def test_config_init_with_empty_ini_file(caplog):
    """ Test avec fichier de config vide """
    with pytest.raises(FileNotFoundError):
        config.AppConfig("")
    for record in caplog.records:
        assert record.levelname == 'CRITICAL'
        assert "Fichier de configuration introuvable ->" in record.message


def test_config_init_with_exception(fakedir_conf_path, caplog):
    """ Test avec fichier de config avec valeur erronee """
    fakefile_appcfg_path = fakedir_conf_path.join("fakefile." + config.CONF_FILEEXT)
    with open(fakefile_appcfg_path, 'w') as f:
        f.write('fakedata')
    with pytest.raises(SystemExit):
        config.AppConfig(fakefile_appcfg_path)
    for record in caplog.records:
        assert record.levelname == 'CRITICAL'
        assert "Impossible de charger le fichier de configuration ->" in record.message


def test_config_init_with_fake_inifile(fakedir_conf_path):
    """ Test avec fichier de config valide contenant une fakesection """
    fakefile_appcfg_path = fakedir_conf_path.join("fakefile." + config.CONF_FILEEXT)
    with open(fakefile_appcfg_path, 'w') as f:
        f.write('[FAKESECTION]\n')
    with pytest.raises(SystemExit):
        config.AppConfig(fakefile_appcfg_path)


def test_config_init_with_fake_log_level(fakedir_conf_path, caplog):
    """ Test avec fichier de config valide contenant une fakesection """
    fakefile_appcfg_path = fakedir_conf_path.join("fakefile." + config.CONF_FILEEXT)
    with open(fakefile_appcfg_path, 'w') as f:
        f.write('[DEFAULT]\n')
        f.write('log_level = BADLEVEL\n')
    with pytest.raises(SystemExit):
        config.AppConfig(fakefile_appcfg_path)
    for record in caplog.records:
        assert record.levelname == 'CRITICAL'
        assert "Impossible de changer le niveau de log" in record.message


def test_config_get(fakefile_appconf_path, caplog):
    """ Test avec fichier de config valide rempli avec des fakes """
    cfg = config.AppConfig(fakefile_appconf_path)
    assert isinstance(cfg, config.AppConfig)
    # Test des valeurs
    assert cfg.get("str1") == "value1"
    assert cfg.get("str2") == "value2"
    assert cfg.get("str3") == "value3"
    assert cfg.get("str4") == "value4"
    assert cfg.get("int1") == 1
    assert cfg.get("int2") == 1.2
    assert cfg.get("bool1") is True
    assert cfg.get("bool2") is False
    # Test exceptions
    with pytest.raises(configparser.NoOptionError):
        cfg.get("nok")
    assert "Option de configuration introuvable ->" in caplog.messages[-1]


########################################


def test_main():
    cfg1 = config.main()
    assert isinstance(cfg1, config.AppConfig)
