#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import configparser
import logging
import logging.config
import functools
import inspect
from pathlib import Path

# Dossier racine du projet
ROOT_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
# Nom de l'application
APP_NAME = "gaia"
# Extension utilisée pour le blocage
# LOCK_EXTENSION = ".lock"
# Nom du dossier de configuration
CONF_DIRNAME = "conf"
# Nom du dossier de configuration
LOGS_DIRNAME = "logs"
# Extension des fichiers de configuration
CONF_FILEEXT = "ini"
# Extension des fichiers de configuration
LOGS_FILEEXT = "log"
# Level par defaut des logs
DEFAULT_LOG_LEVEL = "DEBUG"
# Format par defaut des logs
DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | @ %(lineno)-3s | %(module)s.%(funcName)s() : %(message)s"
# Chemin du fichier de configuration APP
APP_INIFILE_PATH = os.path.join(ROOT_PATH, os.path.join(CONF_DIRNAME, "app" + "." + CONF_FILEEXT))
# Chemin du fichier de configuration APP
LOG_INIFILE_PATH = os.path.join(ROOT_PATH, os.path.join(CONF_DIRNAME, "log" + "." + CONF_FILEEXT))
# Chemin du log de l'application
APP_LOGFILE_PATH = os.path.join(ROOT_PATH, os.path.join(LOGS_DIRNAME, APP_NAME + "." + LOGS_FILEEXT))
# Chemin du log des erreurs de l'application
ERRORS_LOGFILE_PATH = os.path.join(ROOT_PATH, os.path.join(LOGS_DIRNAME, APP_NAME + "_errors" + "." + LOGS_FILEEXT))
# Chemin du log  de l'initialisation de l'application (basicConfig)
START_LOGFILE_PATH = os.path.join(ROOT_PATH, os.path.join(LOGS_DIRNAME, APP_NAME + "_start" + "." + LOGS_FILEEXT))

log = logging.getLogger()

###########################################################################


class LogConfig(object):

    __instance = None

    def __new__(cls, *args, **kwargs):
        """ Singleton
        Returns:
            object: Instance
        """
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, _log_inifile_path):
        """ Initialisation du logger
        Args:
            _log_inifile_path (str): chemin du fichier de configuration
        """
        self._log_inifile_path = _log_inifile_path

        logging.basicConfig(filename=START_LOGFILE_PATH,
                            level=logging.getLevelName(DEFAULT_LOG_LEVEL),
                            format=DEFAULT_LOG_FORMAT)

        if not os.path.exists(self._log_inifile_path):
            log.critical(f"Fichier de configuration du logger introuvable -> {self._log_inifile_path}")
            raise FileNotFoundError(self._log_inifile_path)
        try:
            logging.config.fileConfig(self._log_inifile_path, defaults={"log_filename": APP_LOGFILE_PATH,
                                                                        "errors_filename": ERRORS_LOGFILE_PATH})
        except Exception:
            log.critical(f"Impossible d'initialiser le logger", exc_info=True)
            raise SystemExit(1)
        log.info(f"-------------------------------------------------")
        log.info(f"-- DEMARRAGE DE L'APPLICATION : {APP_NAME.upper()}")
        log.info(f"-------------------------------------------------")


###########################################################################


class LogConfigFormatter(logging.Formatter):  # pragma: no cover
    """ Surcharge du logging.Formatter pour gerer correctement les decorateurs """
    def format(self, record):
        if hasattr(record, 'func_name_override'):
            record.funcName = record.func_name_override
        if hasattr(record, 'func_module_override'):
            record.module = record.func_module_override
        if hasattr(record, 'func_lineno_override'):
            record.lineno = record.func_lineno_override
        return super(LogConfigFormatter, self).format(record)


def fdebug(func):  # pragma: no cover
    """ Debug de fonction avec signature et valeur de retour
    Args:
        func (func): Fonction décorée
    Returns:
        object: _debug()
    """
    @functools.wraps(func)
    def _debug(*args, **kwargs):
        bound_args = inspect.signature(func).bind(*args, **kwargs)
        bound_args.apply_defaults()
        extra_dict = {
            'func_name_override': func.__name__,
            'func_module_override': func.__module__,
            'func_lineno_override': inspect.unwrap(func).__code__.co_firstlineno
        }
        for k, v in bound_args.arguments.items():
            if k != "self":
                log.debug(f"Arg => {k} = {v!r}", extra=extra_dict)
        value = func(*args, **kwargs)
        if value is not None:
            log.debug(f"Ret => {value!r}", extra=extra_dict)
        return value
    return _debug

###########################################################################


class AppConfig(object):

    __instance = None

    def __new__(cls, *args, **kwargs):
        """ Singleton
        Returns:
            object: Instance
        """
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self, _app_inifile_path):
        """ Initialisation de la configuration applicative
        Args:
            _app_inifile_path (str): chemin du fichier de configuration
        """
        self._app_inifile_path = _app_inifile_path
        self.log_level_num = None
        # Ouverture fichier configuration APP
        try:
            self.parser = configparser.ConfigParser()
            self.parser.read_file(open(self._app_inifile_path))
        except FileNotFoundError:
            log.critical(f"Fichier de configuration introuvable -> {self._app_inifile_path}",
                         exc_info=False)
            raise FileNotFoundError(self._app_inifile_path)
        except Exception:
            log.critical(f"Impossible de charger le fichier de configuration -> {self._app_inifile_path}",
                         exc_info=True)
            raise SystemExit(1)
        # Mise jour jour du niveau de log en fonction de la configuration APP
        try:
            self.set_log_level(self.get("log_level"))
        except Exception:
            log.critical(f"Impossible de changer le niveau de log", exc_info=True)
            raise SystemExit(1)

    def get(self, key):
        """ Renvoi de la valeur dune cle de configuration
        Args:
            key (str): Cle de configuration
        Raises:
            configparser.NoOptionError: Option absente
        Returns:
            str: Valeur correspondant a la cle
        """
        if not self.parser.has_option(configparser.DEFAULTSECT, key):
            log.error(f"Option de configuration introuvable -> {key}")
            raise configparser.NoOptionError(configparser.DEFAULTSECT, key)
        v = self.parser.get(configparser.DEFAULTSECT, key)
        # Return int
        try:
            int(v)
            if float(v).is_integer():
                return self.parser.getint(configparser.DEFAULTSECT, key)
        except ValueError:
            pass
        # Return float
        try:
            float(v)
            if not float(v).is_integer():
                return self.parser.getfloat(configparser.DEFAULTSECT, key)
        except ValueError:
            pass
        # Return bool
        if v.lower() in ("true", "false"):
            return self.parser.getboolean(configparser.DEFAULTSECT, key)
        # Return str
        else:
            return v

    def set_log_level(self, log_level):
        """ Definition du niveau de log
        Args:
            self:
            log_level (str): niveau de log
        """
        self.log_level_num = logging.getLevelName(log_level)
        log.setLevel(self.log_level_num)
        log.info(f"Niveau de log -> {log_level}")

###########################################################################


def main():
    # logconfig = LogConfig(LOG_INIFILE_PATH)
    LogConfig(LOG_INIFILE_PATH)
    cfg = AppConfig(APP_INIFILE_PATH)
    return cfg


###########################################################################


if __name__ == "__main__":  # pragma: no cover
    main()
