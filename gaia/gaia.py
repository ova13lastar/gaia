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
            # # Chargement de la configuration addict
            # self.addict_conf = ydt.load_ini_file(os.path.join('.', os.path.join(CONF_DIR_NAME, ADDICT_CONF_FILE_NAME)))
            # # Chemin racine ou se trouvent les elements a traiter
            # self.root_path = self._init_root_path()
            # # Chemin des archives
            # self.archives_path = self._init_binding_folders_path(self.app_conf["dirnames"]["archives"])
            # # Chemin des rejets
            # self.rejets_path = self._init_binding_folders_path(self.app_conf["dirnames"]["rejets"])
            # # Initialisations diverses
            # self.attachments_extensions = ydt.get_ini_tuple(self.addict_conf.get("attachments", "extensions"))
            # self.curpath = None
            # self.files = None
            self.infodata = None
        except:
            log.exception(f"{FATAL_ERROR} : echec de l'initialiation de la classe {__name__}")
            sys.exit(1)

    def app_conf(self):
        return self.app_conf

    def check_infodata(self):
        # print(self.app_conf)
        print(infodata_.InfoData(os.path.join("D:/Python_dev/gaia_src/RENTE/2019080220080400001", INFODATA_FILE_NAME)))

    @ydt.fdebug
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
            # ROOT : On verifie la presence de fichiers a la racine
            if self.curpath == self.root_path:
                self._check_files_in_root_folder(self.files)
            # -------------------------------------------------
            # Si directories contient d'autres repertoires : on laisse le dossier de cote (continue)
            elif len(directories) > 0:
                self._check_directories(directories, self.files)
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
                # FICHIER LOCKED : Si un des fichiers est en cours d'utilisation : on laisse le dossier de cote (continue)
                if [f for f in self.files if ydt.check_file_lock(os.path.join(self.curpath, f))]:
                    for f in self.files:
                        if ydt.check_file_lock(os.path.join(self.curpath, f)):
                            log.info(f"Un fichier est en cours d'utilisation : {os.path.join(self.curpath, f)}")
                    continue
                # -----------------
                # Chargement du fichier infodata.gaia du dossier en cours
                self.infodata = infodata_.InfoData(os.path.join(self.curpath, INFODATA_FILE_NAME))
                # On cree une list des fichiers en minuscule
                files_lower = [item.lower() for item in self.files]
                # On verifie si il manque des fichiers
                self._check_missing_files(files_lower)
                # On verifie si le fichier ini est present et unique
                self._check_ini_file(files_lower)
                # On verifie si le nombre d'attachments est valide
                self._check_attachments_count(files_lower)
                # On verifie si les attachments ont une extension valide
                self._check_attachments_extensions(files_lower)
                # -------------------------------------------------
                # SI ERREUR : On enregistre la tentative dans le fichier infodata
                if self.infodata.get_error_count() > 0:
                    self.infodata.add_tentative()
                # SINON : L'injection semble possible
                else:
                    log.info(f"===> INJECTION POSSIBLE <===")
                    self.infodata.clear_error_msg_list()
                    try:
                        log.info("-------------------------------------------------")
                        log.info(f"LOCK du repertoire : {self.curpath}")
                        locked_path = ydt.lock(self.curpath)
                        addict = addict_.Addict(locked_path)
                        if addict.check_ini() and addict.check_attachments():
                            addict.inject()
                    except Exception as e:
                        log.exception(f"Erreur de l'injection ADDICT : {e}")
                    finally:
                        log.info(f"UNLOCK du repertoire : {self.curpath}")
                        ydt.unlock(self.curpath + LOCK_EXTENSION)
                    # break

    # -------------------------------------------------

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

    @ydt.fdebug
    def _check_files_in_root_folder(self, files):
        """ Permet de verifier et tracer si des fichiers sont present dans le root_path

        Args:
            files (files): List des fichiers present a la racine
        """
        if len(files) > 0:
            log.warning(f"Des fichiers ont ete detectes ({len(files)}) dans le repertoire de base : {self.curpath}")
            for f in files:
                log.warning(f"| -- {f}")

    @ydt.fdebug
    def _check_directories(self, directories, files):
        log.info(f"directories contient d'autres repertoires :")
        for d in directories:
            log.info(f"| -- {d}")
        if len(files) > 0:
            log.warning(f"directories contient aussi des fichiers :")
            for f in files:
                log.warning(f"| -- {f}")

    @ydt.fdebug
    def _check_missing_files(self, files):
        """ Permet de verifier si des fichiers obligatoires sont manquants

        Args:
            files ([list]): List des fichiers à vérifier
        """
        if INFODATA_FILE_NAME in files:
            files.remove(INFODATA_FILE_NAME)
        if len(files) < int(self.app_conf["utils"]["min_files_by_folder"]):
            self.infodata.add_error_msg(f"Nombre de fichiers trop faible : {len(files)}")
            log.error(self.infodata.get_last_msg())
            for f in files:
                log.error(f"| -- {f}")

    @ydt.fdebug
    def _check_ini_file(self, files):
        """ Permet de verifier si fichier ini present et unique

        Args:
            files ([list]): List des fichiers à vérifier
        """
        if INFODATA_FILE_NAME in files:
            files.remove(INFODATA_FILE_NAME)
        if not [f for f in files if f.endswith(CONF_FILE_EXTENSION)]:
            self.infodata.add_error_msg(f'Pas de fichier {CONF_FILE_EXTENSION} detecte')
            log.error(self.infodata.get_last_msg())
        inifile_count = sum(1 for f in files if f.endswith(CONF_FILE_EXTENSION))
        if inifile_count > 1:
            self.infodata.add_error_msg(f'Plusieurs fichiers {CONF_FILE_EXTENSION} ({inifile_count}) detectes')
            log.error(self.infodata.get_last_msg())

    @ydt.fdebug
    def _check_attachments_count(self, files):
        """ Permet de verifier si le nombre d'attachments est correct

        Args:
            files ([list]): List des fichiers à vérifier
        """
        if INFODATA_FILE_NAME in files:
            files.remove(INFODATA_FILE_NAME)
        attachements_count = sum(1 for f in files if f.endswith(self.attachments_extensions) and not f.endswith(CONF_FILE_EXTENSION))
        if int(attachements_count) > self.addict_conf.getint("attachments", "max_files"):
            self.infodata.add_error_msg(f"Nombre de fichiers joints trop grand : {attachements_count}")
            log.error(self.infodata.get_last_msg())
        if int(attachements_count) < 1:
            self.infodata.add_error_msg(f"Nombre de fichier joints trop petit : {attachements_count}")
            log.error(self.infodata.get_last_msg())

    @ydt.fdebug
    def _check_attachments_extensions(self, files):
        """ Permet de verifier si les attachments ont bien une extension valide

        Args:
            files ([list]): List des fichiers à vérifier
        """
        error_count = 0
        error_files = []
        if INFODATA_FILE_NAME in files:
            files.remove(INFODATA_FILE_NAME)
        for f in files:
            if f.endswith(CONF_FILE_EXTENSION):
                files.remove(f)
                continue
            if not f.endswith(self.attachments_extensions):
                error_files.append(f)
                error_count += 1
        if error_count > 0:
            self.infodata.add_error_msg(f"Nb de fichiers avec une extension incorrecte : {error_count}")
            log.error(self.infodata.get_last_msg())
            for f in error_files:
                log.error(f"| -- {f}")
