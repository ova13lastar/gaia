#!/usr/bin/env python

import os
import sys
import configparser
import math
import msvcrt
import functools
import inspect
import logging
import logging.config
import traceback

from constants import *

# Recuperation du logger
log = logging.getLogger()


class YdLogFormatter(logging.Formatter):
    """ Surcharge du logging.Formatter pour gerer correctement les decorateurs
    """

    def format(self, record):
        if hasattr(record, 'func_name_override'):
            record.funcName = record.func_name_override
        if hasattr(record, 'func_module_override'):
            record.module = record.func_module_override
        if hasattr(record, 'func_lineno_override'):
            record.lineno = record.func_lineno_override
        return super(YdLogFormatter, self).format(record)


def init_logger():
    """  Initialisation du logger

    Returns:
        dict: Objet log
    """
    try:
        log = logging.getLogger()
        logging.config.fileConfig(LOG_CONF_PATH, defaults={'logfilename': APP_NAME + '.log'})
        return log
    except Exception as e:
        print(f"{FATAL_ERROR} : lors de l'initialiation de la configuration {LOG_CONF_PATH}")
        print(f"{e}")
        print(traceback.format_exc())
        sys.exit(1)


def fdebug(func):
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


@fdebug
def load_ini_file(inifile_path):
    """ Chargement d'un fichier ini dans un dictionnaire

    Args:
        inifile_path (str): Chemin du fichier

    Returns:
        configparser object: Objet contenant le contenu du fichier ini
    """
    try:
        c = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        inifile_parsed = c.read(inifile_path)
        log.debug(f"inifile_parsed = {inifile_parsed}")
    except configparser.ParsingError:
        log.error(f"Erreur lors du parsing du fichier : {inifile_path}")
        raise
    except:
        log.error(f"Impossible de charger le fichier : {inifile_path}")
        raise
    else:
        return c


def get_ini_tuple(item, type_="str"):
    """ Renvoi un tuple d'un item issu d'un fichier ini

    Args:
        item (str): Item issu d'un fichier ini
        type_ (str): Permet de spécifier le format en sortie (str par defaut)

    Returns:
        tuple: Tuple convertit
    """
    item = item.split(',')
    if type_ == "int":
        item = [int(i) for i in item]
    return tuple(item)


@fdebug
def lock(path):
    """ Permet de bloquer un fichier/dossier en rajoutant l'extension de lock

    Args:
        path (str): Chemin du fichier/dossier a bloquer

    Returns:
        str: Chemin du fichier/dossier bloque
    """
    locked_path = path + LOCK_EXTENSION
    log.debug(f"locked_path = {locked_path}")
    if path.endswith(LOCK_EXTENSION) or os.path.exists(locked_path):
        log.error(f"Le fichier/dossier est deja bloque : {locked_path}")
        raise
    if not os.path.exists(path):
        log.error(f"Le fichier/dossier suivant n'existe pas : {path}")
        raise
    try:
        os.rename(path, locked_path)
    except FileNotFoundError:
        log.error(f"Le fichier/dossier est introuvable : {path}")
        raise
    except:
        log.error(f"Erreur lors du blocage du fichier/dossier : {path}")
        raise
    else:
        return locked_path


@fdebug
def unlock(locked_path):
    """ Permet de debloquer un fichier/dossier en supprimant l'extension de lock

    Args:
        _path (str): Chemin du fichier/dossier a debloquer

    Returns:
        str: Chemin du fichier/dossier debloque
    """
    unlocked_path = os.path.splitext(locked_path)[0]
    log.debug(f"unlocked_path = {unlocked_path}")
    if not locked_path.endswith(LOCK_EXTENSION) or os.path.exists(unlocked_path):
        log.error(f"Le fichier/dossier est deja debloque : {unlocked_path}")
        raise
    if not os.path.exists(locked_path):
        log.error(f"Le fichier/dossier suivant n'existe pas : {locked_path}")
        raise
    try:
        os.rename(locked_path, unlocked_path)
    except FileNotFoundError:
        log.error(f"Le fichier/dossier est introuvable : {locked_path}")
        raise
    except:
        log.error(f"Erreur lors du deblocage du fichier/dossier : {locked_path}")
        raise
    else:
        return unlocked_path


# @fdebug
def check_file_lock(file_path):
    """ Verifie si un fichier est bloque par un autre processus (True) ou s'il est accessible (False)

    Args:

        _path (str): Chemin du fichier a verifie

    Returns:
        bool: Renvoi True si fichier bloque, False si peut etre modifie
    """
    try:
        fd = os.open(file_path, os.O_APPEND | os.O_EXCL | os.O_RDWR)
    except OSError:
        return True
    try:
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        os.close(fd)
        return False
    except (OSError, IOError):
        os.close(fd)
        return True


@fdebug
def check_valid_nir(nir):
    """ Verifie si un NIR est valide

    Args:

        nir (str): Le NIR

    Returns:
        bool: Renvoi True si valide, False si invalide
    """
    # On gere les cas Corses
    nir_cle = nir.replace('A', '0')
    nir_cle = nir.replace('B', '0')
    # On verifie d'abord que nir est un entier
    try:
        int(nir_cle)
    except ValueError:
        log.error("Un NIR ne peut contenir que des chiffres !")
        return False
    # On verifie la longueur exacte
    if len(nir) != 15:
        log.error("Un NIR doit faire exactement 15 caractères (NIR+CLE) !")
        return False
    # On verifie que la cle du nir est valide (http://fr.wikipedia.org/wiki/Numero_de_Securite_sociale#Unicit.C3.A9)
    nir = nir_cle[0:13]
    cle = nir_cle[13:15]
    cle_valid = (97 - (int(nir) % 97))
    if int(cle) != int(cle_valid):
        return False
    return True


@fdebug
def convert_filesize(size):
    """ Convertit une taille de fichier : octet vers human readable

    Args:

        size (str): Taille en bit

    Returns:
        str: Taille en human readable
    """
    if (size == 0):
        return '0B'
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return '%s %s' % (s, size_name[i])
