#!/usr/bin/env python

import os
import logging
import datetime
import json

from constants import *
import ydtools as ydt
import gaia

# Recuperation du logger
log = logging.getLogger()


class InfoData():

    def __init__(self, infodata_file_path):
        print(gaia.Gaia.app_conf())
        try:
            # Initialisations nominales
            self.infodata_file_path = infodata_file_path
            self.infodata = {
                'tentative_count': 0,
                'tentative_datetime': '',
                'error_msg_list': []
            }
            # Si le fichier n existe pas : on le cree avec des infodata de base
            if not os.path.exists(self.infodata_file_path):
                log.info(f"{os.path.basename(self.infodata_file_path)} n'existait pas : Creation ...")
                self._write()
            # Sinon on recupere les infodata qu'il contient
            else:
                log.info(f"{os.path.basename(self.infodata_file_path)} existe")
                self.infodata = self._read()
                self.clear_error_msg_list()
        except:
            log.critical(f"Echec de l'initialiation de la classe {__name__}")
            log.exception(f"{e}")
            raise

    def get_error_count(self):
        """ Permet de renvoyer le nombre de messages d'erreurs enregistres

        Returns:
            [int]: nombre de messages d'erreurs
        """
        return len(self.infodata["error_msg_list"])

    def get_last_msg(self):
        """ Permet de renvoyer le dernier message enregistre

        Returns:
            [str]: dernier message enregistre
        """
        return '' if self.get_error_count() == 0 else self.infodata["error_msg_list"][-1]

    @ydt.fdebug
    def add_error_msg(self, msg):
        """ Permet d'enregistrer le message passe en parametre

        Args:
            msg (str): message a enregistrer
        """
        self.infodata["error_msg_list"].append(msg)
        self._write()

    @ydt.fdebug
    def clear_error_msg_list(self):
        """ Permet de reinitialiser les messages du fichier infodata
        """
        self.infodata["error_msg_list"].clear()
        self._write()

    @ydt.fdebug
    def add_tentative(self):
        """ Permet d'incrémenter le compteur des tentatives + datetime
        """
        self.infodata["tentative_count"] += 1
        self.infodata["tentative_datetime"] = str(datetime.datetime.now())
        self._write()

    # -------------------------------------------------

    @ydt.fdebug
    def _read(self):
        try:
            with open(self.infodata_file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            log.exception(f"Erreur lecture fichier {os.path.basename(self.infodata_file_path)} : {e}")
            raise

    @ydt.fdebug
    def _write(self):
        try:
            with open(self.infodata_file_path, 'w') as f:
                json.dump(self.infodata, f, indent=4)
        except Exception as e:
            log.exception(f"Erreur ecriture fichier {os.path.basename(self.infodata_file_path)} : {e}")
            raise
