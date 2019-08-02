#!/usr/bin/env python

import os
import sys
import logging

from constants import *
import ydtools as ydt
import addict as addict_
import infodata as infodata_

# Recuperation du logger
log = logging.getLogger()


class Gaia:

    def __init__(self):
        try:
            # Chargement de la configuration applicative
            self.app_conf = ydt.load_ini_file(os.path.join('.', os.path.join(CONF_DIR_NAME, APP_CONF_FILE_NAME)))
            # Chargement de la configuration addict
            self.addict_conf = ydt.load_ini_file(os.path.join('.', os.path.join(CONF_DIR_NAME, ADDICT_CONF_FILE_NAME)))
            # Chemin racine ou se trouvent les elements a traiter
            self.root_path = self._init_root_path()
            # Chemin des archives
            self.archives_path = self._init_binding_folders_path(self.app_conf["dirnames"]["archives"])
            # Chemin des rejets
            self.rejets_path = self._init_binding_folders_path(self.app_conf["dirnames"]["rejets"])
            # Initialisations diverses
            self.attachments_extensions = ydt.get_ini_tuple(self.addict_conf.get("attachments", "extensions"))
            self.curpath = None
            self.files = None
        except:
            log.exception(f"{FATAL_ERROR} : echec de l'initialiation de la classe {__name__}")
            sys.exit(1)

    def scan_root_path(self):
        """ Scan complet du chemin racine (root_path)
        """
        for self.curpath, directories, self.files in os.walk(self.root_path):
            # ARCHIVES / REJETS :  On ne fait rien (continue)
            if self.curpath.startswith(self.archives_path) or self.curpath.startswith(self.rejets_path):
                continue
            # On log le dossier en cours
            log.info("-------------------------------------------------")
            log.info(f"self.curpath = {self.curpath}")
            # -------------------------------------------------
            # ROOT : On log la presence de fichiers a la racine
            if self.curpath == self.root_path and len(self.files) > 0:
                log.warning(f"Fichiers detectes ({len(self.files)}) dans le repertoire de base : {self.curpath}")
                for f in self.files:
                    log.warning(f"| -- {f}")
            # -------------------------------------------------
            # Si directories contient d'autres repertoires : on laisse le dossier de cote (continue)
            elif len(directories) > 0:
                log.info(f"directories contient d'autres repertoires :")
                for d in directories:
                    log.info(f"| -- {d}")
                if len(self.files) > 0:
                    log.info(f"directories contient aussi des fichiers :")
                    for f in self.files:
                        log.info(f"| -- {f}")
                continue
            # -------------------------------------------------
            # DOSSIERS : On verifie la coherence des dossiers
            else:
                # -----------------
                # DOSSIER LOCKED : Si dossier deja bloque : on sort de la boucle (break)
                if self.curpath.endswith(LOCK_EXTENSION):
                    log.warning(f"Dossier deja bloque : {self.curpath}")
                    break
                # -----------------
                # VARIABLES : On reinitialise la list des messages
                tentative_msg = []
                # On récupère les infodata du dossier (fichier .json)
                infodata = infodata_.InfoData(os.path.join(self.curpath, self.app_conf.get("filenames", "infodata")))
                # On cree une list des fichiers en minuscule
                files_lower = [item.lower() for item in self.files]
                # On recupere le nombre de fichiers ini
                inifile_count = sum(1 for f in files_lower if f.endswith(self.addict_conf.get("ini", "extension")))
                # -----------------
                # FICHIER LOCKED : Si un des fichiers est en cours d'utilisation : on laisse le dossier de cote (continue)
                if [f for f in self.files if ydt.check_file_lock(os.path.join(self.curpath, f))]:
                    for f in self.files:
                        if ydt.check_file_lock(os.path.join(self.curpath, f)):
                            log.info(f"Un fichier est en cours d'utilisation : {os.path.join(self.curpath, f)}")
                    continue
                # -----------------
                # WARNINGS : Si il manque des fichiers : on log
                if len(self.files) < int(self.app_conf["utils"]["min_files_by_folder"]):
                    tentative_msg.append(f"Nombre de fichiers trop faible ({len(self.files)})")
                    for f in self.files:
                        log.warning(f"| -- {f}")
                # Sinon si il manque le fichier .ini : on log
                elif not [f for f in files_lower if f.endswith(self.addict_conf.get("ini", "extension"))]:
                    tentative_msg.append(f'Pas de fichier {self.addict_conf.get("ini", "extension")} detecte')
                # Sinon si il y a plus d'un fichier .ini : on log
                elif inifile_count > 1:
                    tentative_msg.append(f'Plusieurs fichiers {self.addict_conf.get("ini", "extension")} ({inifile_count}) detectes')
                # Sinon si des fichiers n'ont pas la bonne extension : on log
                elif not [f for f in files_lower if f.endswith(self.attachments_extensions)]:
                    tentative_msg.append(f"Fichiers avec une extension incorrecte detectes")
                    for f in self.files:
                        log.warning(f"| -- {f}")
                # Sinon si il y a plus de 10 fichiers : on log
                elif [f for f in files_lower if f.endswith(self.attachments_extensions) and len(self.files)-1 > self.addict_conf.getint("attachments", "max_files")]:
                    tentative_msg.append(f"Nombre de fichiers joints trop grand ({len(self.files)-1})")
                # On enregistre la tentative dans le fichier infodata
                if len(tentative_msg) > 0:
                    infodata.set_tentative(tentative_msg)
                # -------------------------------------------------
                # SINON : on rajoute le dossier dans la list des dossiers a gerer
                else:
                    log.info(f"INJECTION POSSIBLE !!!")
                    try:
                        log.info("-------------------------------------------------")
                        log.info(f"LOCK du repertoire : {self.curpath}")
                        locked_path = ydt.lock(self.curpath)
                        addict = addict_.Addict(locked_path, self.addict_conf)
                        if addict.check_ini() and addict.check_attachments():
                            addict.inject()
                    except Exception as e:
                        log.exception(f"Erreur de l'injection ADDICT : {e}")
                    finally:
                        log.info(f"UNLOCK du repertoire : {self.curpath}")
                        ydt.unlock(self.curpath + LOCK_EXTENSION)
                    break

    @ydt.fdebug
    def _init_root_path(self):
        """ Initialisation du chemin racine (root_path)

        Returns:
            str: Chemin racine (root_path)
        """
        try:
            root_path = os.path.normpath(self.app_conf["general"]["root_path"])  # -> Chemin racine ou se trouvent les elements a traiter
            if os.path.exists(root_path):
                return root_path
            else:
                log.critical(f"{FATAL_ERROR} : le chemin racine n'existe pas : {root_path}")
                raise
        except:
            log.critical(f"{FATAL_ERROR} : echec initialisation du chemin racine : {root_path}")
            raise

    @ydt.fdebug
    def _init_binding_folders_path(self, folder_name):
        """ Initialisation des dossiers obligatoires

        Args:
            folder_name (str): Nom du dossier obligatoire

        Returns:
            str: Chemin du dossier obligatoire
        """
        try:
            folder_path = os.path.join(self.root_path, folder_name)
            os.makedirs(folder_path)
            log.info(f"Creation du dossier des {folder_name} : {folder_path}")
        except FileExistsError:
            log.info(f"Le dossier des {folder_name} existe bien : {folder_path}")
        except:
            log.critical(f"{FATAL_ERROR} : lors de la creation du dossier des {folder_name} : {archives_path}")
            raise
        return folder_path
