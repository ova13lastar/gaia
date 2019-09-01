#!/usr/bin/env python

import os
import logging
import datetime
import configparser

from constants import *
import ydtools as ydt

# Recuperation du logger
log = logging.getLogger()


class InfoData():

    def __init__(self, infodata_file_path):
        try:
            # Initialisations nominales
            self.infodata_file_path = infodata_file_path
            self._error_count = 0
            self._last_msg = None
            # Initialisation du configparser
            self.infodata = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
            # Si le fichier n existe pas : on le cree avec des infodata de base
            if not os.path.exists(self.infodata_file_path):
                log.info(f"{os.path.basename(self.infodata_file_path)} n'existait pas : Creation ...")
                self.infodata.add_section("tentatives")
                self.infodata.set("tentatives", "nb", str(0))
                self.infodata.set("tentatives", "datetime", "")
                self._write_in_file()
            else:
                log.info(f"{os.path.basename(self.infodata_file_path)} existe")
            # On lit les infos du fichier infodata
            self.infodata.read(self.infodata_file_path)
            # On vide le tableau des msg
            self.infodata.set("tentatives", "msg", "")
        except:
            log.critical(f"Echec de l'initialiation de la classe {__name__}")
            raise

    @ydt.fdebug
    def get_error_count(self):
        """ Permet de renvoyer le nombre d'erreurs enregistrees

        Returns:
            [int]: nombre d'erreurs
        """
        return self._error_count

    @ydt.fdebug
    def get_last_msg(self):
        """ Permet de renvoyer le dernier message enregistre

        Returns:
            [str]: dernier message enregistre
        """
        return self._last_msg

    @ydt.fdebug
    def log_msg(self, msg):
        """ Permet d'enregistrer et tracer le message passe en parametre

        Args:
            msg (str): message a enregistrer
        """
        self._last_msg = msg
        self._set_tentative_msg_list(msg)

    @ydt.fdebug
    def add_tentative(self):
        tentative_nb = self.infodata.getint("tentatives", "nb")
        self.infodata.set("tentatives", "nb", str(tentative_nb + 1))
        self.infodata.set("tentatives", "datetime", str(datetime.datetime.now()))
        self._write_in_file()

    # -------------------------------------------------

    @ydt.fdebug
    def _get_tentative_msg_list(self):
        tentative_msg_list = self.infodata.get("tentatives", "msg").split(",")
        return list() if '' in tentative_msg_list else tentative_msg_list

    @ydt.fdebug
    def _set_tentative_msg_list(self, msg):
        tentative_msg_list = self._get_tentative_msg_list()
        self.infodata.set("tentatives", "msg", ",".join(tentative_msg_list))
        self._error_count += 1

    @ydt.fdebug
    def _write_in_file(self):
        try:
            with open(self.infodata_file_path, 'w') as f:
                self.infodata.write(f)
        except Exception as e:
            log.exception(f"Erreur ecriture fichier {os.path.basename(self.infodata_file_path)} : {e}")
            raise
