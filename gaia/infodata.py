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
        self.infodata_file_path = infodata_file_path
        self.infodata = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        # Si le fichier n existe pas : on le cree avec des infodata de base
        if not os.path.exists(self.infodata_file_path):
            log.info(f"Le fichier {os.path.basename(self.infodata_file_path)} n'existe pas")
            self.infodata.add_section("tentatives")
            self.infodata.set("tentatives", "nb", str(1))
            self.infodata.set("tentatives", "datetime", str(datetime.datetime.now()))
            self.infodata.set("tentatives", "msg", "")
            self._write_in_file()
        else:
            log.info(f"Le fichier {os.path.basename(self.infodata_file_path)} existe")
        # On lit les infos du fichier infodata
        self.infodata.read(self.infodata_file_path)

    def set_tentative(self, tentative_msg):
        log.warning(tentative_msg[-1])
        tentative_nb = self.infodata.getint("tentatives", "nb")
        self.infodata.set("tentatives", "nb", str(tentative_nb + 1))
        self.infodata.set("tentatives", "datetime", str(datetime.datetime.now()))
        self.infodata.set("tentatives", "msg", ",".join(tentative_msg))
        self._write_in_file()

    def _write_in_file(self):
        try:
            with open(self.infodata_file_path, 'w') as f:
                self.infodata.write(f)
        except Exception as e:
            log.exception(f"Erreur ecriture fichier {os.path.basename(self.infodata_file_path)} : {e}")
            raise
