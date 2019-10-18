#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging

import src.gaia.config as config
import src.gaia.ydutils as ydutils

log = logging.getLogger()
cfg = config.main()

###########################################################################


class Gaia:

    def __init__(self, src_path):
        """ Initialisation de gaia

        Args:
            src_path (str): Chemin source principal
        """
        self.infodata = None
        self.curpath = None
        self.directories = None
        self.files = None
        # Verification existence src_path
        self.src_path = src_path
        if not os.path.exists(self.src_path):
            log.error(f"Chemin absolu du repertoire GAIA introuvable -> {self.src_path}")
            raise FileNotFoundError(self.src_path)
        # Initialisation des dossiers obligatoires
        # self.archives_path = self._init_binding_folders_path(cfg.get("archives_dirname"))
        # self.rejets_path = self._init_binding_folders_path(cfg.get("rejets_dirname"))

    def scan_src_path(self):
        """ Scan complet du chemin racine (self.src_path) """
        for self.curpath, self.directories, self.files in os.walk(self.src_path):
            # ARCHIVES / REJETS :  On ne fait rien (continue)
            # if self.curpath.startswith(self.archives_path) or self.curpath.startswith(self.rejets_path):
            #     continue
            # On log le dossier en cours
            self.curpath = os.path.normpath(self.curpath)
            log.info("-------------------------------------------------")
            log.info(f"self.curpath = {self.curpath}")
            # -------------------------------------------------
            # ROOT : On verifie la presence de fichiers a la racine
            if self.curpath == self.src_path:
                self._check_files_in_src_folder(self.files)
            # -------------------------------------------------
            # DOSSIERS : On verifie la coherence des dossiers
            else:
                # -----------------
                # Si un dossier contient d'autres dossier : on le trace sans rien faire
                self._check_directories(self.directories, self.files)
                # -----------------
                # DOSSIER LOCKED : Si dossier deja bloque : on sort de la boucle (break)
                if ydutils.is_locked_dir(self.curpath):
                    break
                if self.curpath.endswith(cfg.get("lock_fileext")):
                    log.warning(f"Dossier deja bloque -> {self.curpath}")
                    break
                # Si un dossier contient d'autres dossier : on le trace sans rien faire
                log.info("OK !!!")

    # @config.fdebug
    # def _init_binding_folders_path(self, folder_name):
    #     """ Initialisation des dossiers obligatoires
    #     Args:
    #         folder_name (str): Nom du dossier obligatoire
    #     Returns:
    #         str: Chemin du dossier obligatoire
    #     """
    #     try:
    #         folder_path = os.path.join(self.src_path, folder_name)
    #         os.makedirs(folder_path)
    #         log.info(f"Creation du dossier des {folder_name} -> {folder_path}")
    #     except FileExistsError:
    #         log.info(f"Le dossier des {folder_name} existe bien -> {folder_path}")
    #     except Exception as e:
    #         log.error(f"Impossible de créer le dossier des {folder_name} -> {folder_path}")
    #         raise
    #     return folder_path

    # @config.fdebug
    @staticmethod
    def _check_files_in_src_folder(files):
        """ Permet de verifier et tracer si des fichiers sont present dans le src_path
        Args:
            files (files): List des fichiers present a la racine
        """
        if len(files) > 0:
            log.warning(f"Des fichiers ont ete detectes dans le repertoire de base -> {len(files)}")
            for f in files:
                log.info(f"| -- {f}")

    # @config.fdebug
    @staticmethod
    def _check_directories(directories, files):
        """ Permet de verifier et tracer si des repertoires sont present dans d'autres repertoires
        Args:
            directories (Sized):
            files (Sized):
        """
        if len(directories) > 0:
            log.info(f"directories contient d'autres repertoires :")
            for d in directories:
                log.info(f"| -- {d}")
            if len(files) > 0:
                log.warning(f"directories contient aussi des fichiers :")
                for f in files:
                    log.info(f"| -- {f}")

    # # @config.fdebug
    # def _is_dir_locked(self, curpath):
    #     """ Permet de verifier et tracer si le curpath est bloque ou non
    #     Args:
    #         curpath (curpath): Chemin du dossier en cours
    #     """
    #     if curpath.endswith(cfg.get("lock_fileext")):
    #         log.warning(f"Dossier deja bloque -> {curpath}")
    #         return True
    #     return False

###########################################################################


def main():  # pragma: no cover
    # Boucle infinie
    while True:
        # Traitement principal
        try:
            g = Gaia(cfg.get("gaia_src_path"))
            g.scan_src_path()
            raise SystemExit(0)
        except Exception as e:
            log.critical(f"ERREUR FATALE : {e}", exc_info=True)
            raise SystemExit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
