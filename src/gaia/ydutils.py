#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import logging

import src.gaia.config as config

log = logging.getLogger()
cfg = config.main()


###########################################################################


def isint(v):
    """ Permet de verifier si la valeur <v> est un entier
    Args:
        v (str): valeur a verifier
    Returns:
        bool: True si entier, sinon False
    """
    try:
        int(v)
        return True if float(v).is_integer() else False
    except ValueError:
        return False


def isfloat(v):
    """ Permet de verifier si la valeur <v> est un flottant
    Args:
         v (str): valeur a verifier
    Returns:
        bool: True si flottant, sinon False
    """
    try:
        float(v)
        return False if float(v).is_integer() else True
    except ValueError:
        return False


@config.fdebug
def isvalid_nir(nir):
    """ Verifie si un NIR est valide
    Args:
        nir (str): Le NIR
    Returns:
        bool: Renvoi True si valide, False si invalide
    """
    # On gere les cas Corses
    nir_cle = nir.replace('A', '0').replace('B', '0')
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
        log.error("La cle du NIR est invalide !")
        return False
    return True


@config.fdebug
def convert_filesize(size):
    """ Convertit une taille de fichier : octet vers human readable
    Args:
        size (SupportFloats): Taille en bit
    Returns:
        str: Taille en human readable
    """
    if size == 0:
        return '0B'
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return '%s %s' % (s, size_name[i])


@config.fdebug
def is_locked_dir(dirpath, logged=True):
    """ Permet de verifier si un dossier est bloque ou non
    Args:
        dirpath (str): Chemin du dossier en cours
        logged (bool) : Log si Vrai
    """
    if dirpath.endswith(cfg.get("lock_fileext")):
        if logged:
            log.warning(f"Dossier deja bloque -> {dirpath}")
        return True
    return False

# @config.fdebug
# def lock(path):
#     """ Permet de bloquer un fichier/dossier en rajoutant l'extension de lock
#     Args:
#         path (str): Chemin du fichier/dossier a bloquer
#     Returns:
#         str: Chemin du fichier/dossier bloque
#     """
#     locked_path = path + LOCK_EXTENSION
#     log.debug(f"locked_path = {locked_path}")
#     if path.endswith(LOCK_EXTENSION) or os.path.exists(locked_path):
#         log.error(f"Le fichier/dossier est deja bloque : {locked_path}")
#         raise
#     if not os.path.exists(path):
#         log.error(f"Le fichier/dossier suivant n'existe pas : {path}")
#         raise
#     try:
#         os.rename(path, locked_path)
#     except FileNotFoundError:
#         log.error(f"Le fichier/dossier est introuvable : {path}")
#         raise
#     except:
#         log.error(f"Erreur lors du blocage du fichier/dossier : {path}")
#         raise
#     else:
#         return locked_path


# @config.fdebug
# def unlock(locked_path):
#     """ Permet de debloquer un fichier/dossier en supprimant l'extension de lock
#     Args:
#         _path (str): Chemin du fichier/dossier a debloquer
#     Returns:
#         str: Chemin du fichier/dossier debloque
#     """
#     unlocked_path = os.path.splitext(locked_path)[0]
#     log.debug(f"unlocked_path = {unlocked_path}")
#     if not locked_path.endswith(LOCK_EXTENSION) or os.path.exists(unlocked_path):
#         log.error(f"Le fichier/dossier est deja debloque : {unlocked_path}")
#         raise
#     if not os.path.exists(locked_path):
#         log.error(f"Le fichier/dossier suivant n'existe pas : {locked_path}")
#         raise
#     try:
#         os.rename(locked_path, unlocked_path)
#     except FileNotFoundError:
#         log.error(f"Le fichier/dossier est introuvable : {locked_path}")
#         raise
#     except:
#         log.error(f"Erreur lors du deblocage du fichier/dossier : {locked_path}")
#         raise
#     else:
#         return unlocked_path


# def check_file_lock(file_path):
#     """ Verifie si un fichier est bloque par un autre processus (True) ou s'il est accessible (False)
#     Args:
#         _path (str): Chemin du fichier a verifie
#     Returns:
#         bool: Renvoi True si fichier bloque, False si peut etre modifie
#     """
#     try:
#         fd = os.open(file_path, os.O_APPEND | os.O_EXCL | os.O_RDWR)
#     except OSError:
#         return True
#     try:
#         msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
#         msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
#         os.close(fd)
#         return False
#     except (OSError, IOError):
#         os.close(fd)
#         return True
