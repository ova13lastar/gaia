#!/usr/bin/env python

import os
import datetime
import logging
import configparser

from constants import *
import ydtools as ydt
import infodata as infodata_

# Recuperation du logger
log = logging.getLogger()


class Addict:

    def __init__(self, folder_path):
        try:
            # Initialisations nominales
            if not os.path.exists(folder_path):
                raise FileNotFoundError()
            self.folder_path = folder_path
            self.data = dict()
            # Chargement de la configuration addict
            self.addict_conf = ydt.load_ini_file(os.path.join('.', os.path.join(CONF_DIR_NAME, ADDICT_CONF_FILE_NAME)))
            # Chargement du fichier infodata.gaia
            self.infodata = infodata_.InfoData(os.path.join(folder_path, INFODATA_FILE_NAME))
            # Chargement du fichier ini de configuration
            self.inifile_name = [f for f in os.listdir(self.folder_path) if f.endswith(CONF_FILE_EXTENSION)][0]
            inifile_path = os.path.join(self.folder_path, self.inifile_name)
            self.ini_conf = ydt.load_ini_file(inifile_path)
            # Initialisations diverses
            self.attachments_paths = [os.path.abspath(f) for f in os.listdir(self.folder_path) if f.endswith(ydt.get_ini_tuple(self.addict_conf.get("attachments", "extensions")))]
        except FileNotFoundError:
            log.critical(f"Le dossier n'existe pas : {folder_path}")
            raise
        except Exception as e:
            log.critical(f"Echec de l'initialiation de la classe {__name__}")
            log.exception(f"{e}")
            raise

    # @ydt.fdebug
    # def get_inifile_path(self):
    #     return os.path.join(self.folder_path, self.inifile_name)

    @ydt.fdebug
    def inject(self):
        log.info(f"!!!!!!!!!!!!!!!!!!!!!! INJECTION !!!!!!!!!!!!!!!!!!!!!")

    @ydt.fdebug
    def check_ini(self):
        try:
            # On verifie la coherence des sections
            self._check_ini_sections()
            # On verifie la coherence des cles
            if self.infodata.get_error_count() == 0:
                self._check_ini_keys()
            # On verifie les keys/values dans chaque section
            if self.infodata.get_error_count() == 0:
                # On verifie le contenu de la section [general]
                self._check_ini_processus()
                self._check_ini_archivage()
                self._check_ini_date_reception()
                self._check_ini_index_metier()
                self._check_ini_nir()
                self._check_ini_nom()
                self._check_ini_siret()
                self._check_ini_finess_ps()
                self._check_ini_date_evenement()
                self._check_ini_num_dossier()
                self._check_ini_commentaire()
                # On verifie le contenu de la section [attachments]
                self._check_ini_attachments()
        except Exception as e:
            log.exception(f"Erreur fonction {__name__} : {e}")
            raise
        finally:
            self.infodata.add_tentative()
        # On renvoie un bool comme resultat
        if self.infodata.get_error_count() == 0:
            return True
        return False

    @ydt.fdebug
    def check_attachments(self):
        return True

    # -------------------------------------------------

    @ydt.fdebug
    def _check_ini_sections(self):
        # On verifie que ini_conf contient qque chose
        if not self.ini_conf.sections():
            self.infodata.add_error_msg(f"Fichier {CONF_FILE_EXTENSION} de configuration vide ou mal charge")
            log.error(self.infodata.get_last_msg())
        # On verifie que les sections existent bien
        for s in ydt.get_ini_tuple(self.addict_conf.get("sections", "main_sections")):
            if not self.ini_conf.has_section(s):
                self.infodata.add_error_msg(f"Fichier {CONF_FILE_EXTENSION} de configuration avec section inexistante : {s}")
                log.error(self.infodata.get_last_msg())

    @ydt.fdebug
    def _check_ini_keys(self):
        # Cles de la section [general]
        for k, v in self.addict_conf.items("general_keys"):
            vbool = self.addict_conf.getboolean("general_keys", k)
            if vbool:
                # On verifie que les valeurs obligatoires de la section sont bien renseignees
                try:
                    if self.ini_conf.get("general", k) == "":
                        self.infodata.add_error_msg(f"Valeur obligatoire manquante pour la cle : {k}=")
                        log.error(self.infodata.get_last_msg())
                # On verifie que les cles obligatoires de la section existent bien
                except configparser.NoOptionError:
                    self.infodata.add_error_msg(f"Cle obligatoire inexistante : {k}=")
                    log.error(self.infodata.get_last_msg())
        # Cles de la section [fichiers]
        for k, v in self.addict_conf.items("attachments_keys"):
            vbool = self.addict_conf.getboolean("attachments_keys", k)
            if vbool:
                # On verifie que les valeurs obligatoires de la section sont bien renseignees
                try:
                    if self.ini_conf.get("fichiers", k) == "":
                        self.infodata.add_error_msg(f"Valeur obligatoire manquante pour la cle : {k}=")
                        log.error(self.infodata.get_last_msg())
                # On verifie que les cles obligatoires de la section existent bien
                except configparser.NoOptionError:
                    self.infodata.add_error_msg(f"Cle obligatoire inexistante : {k}=")
                    log.error(self.infodata.get_last_msg())

    @ydt.fdebug
    def _check_ini_processus(self):
        data_id = "processus"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        # On verifie que les cles sont renseignes pour les processus particuliers (regles metiers)
        if self.data[data_id] not in self.addict_conf.items("general_processus_key_rules") and \
                self.ini_conf.get("general", "nir") == "" and \
                self.ini_conf.get("general", "nom") == "":
            self.infodata.add_error_msg(f"Valeur obligatoire manquante les cles nir= et nom= alors que {data_id}={self.data[data_id]}")
            log.error(self.infodata.get_last_msg())
        # On verifie que le processus correspond a un processus valide
        if self.data[data_id] not in ydt.get_ini_tuple(self.addict_conf.get("general", data_id)):
            self.infodata.add_error_msg(f"Valeur incorrecte : {data_id}={self.data[data_id]}")
            log.error(self.infodata.get_last_msg())

    @ydt.fdebug
    def _check_ini_archivage(self):
        data_id = "archivage"
        self.data[data_id] = int(
            str.strip(self.ini_conf.get("general", data_id)))
        if self.data[data_id] not in ydt.get_ini_tuple(self.addict_conf.get("general", data_id), "int"):
            self.infodata.add_error_msg(f"Valeur incorrecte pour {data_id}={self.data[data_id]}")
            log.error(self.infodata.get_last_msg())

    @ydt.fdebug
    def _check_ini_date_reception(self):
        data_id = "date_reception"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            # On verifie que la date est valide
            try:
                datetime.datetime.strptime(self.data[data_id], "%Y%m%d")
            except ValueError:
                self.infodata.add_error_msg(f"Date incorrecte (format: AAAAMMJJ) pour {data_id}={self.data[data_id]}")
                log.error(self.infodata.get_last_msg())
            else:
                # On verifie que la date n'est pas superieure a la date du jour
                if datetime.datetime.strptime(self.data[data_id], "%Y%m%d") > datetime.datetime.now():
                    self.infodata.add_error_msg(f"Date superieure a la date du jour pour {data_id}={self.data[data_id]}")

    @ydt.fdebug
    def _check_ini_index_metier(self):
        data_id = "index_metier"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            # On verifie la longueur max
            if len(self.data[data_id]) > 20:
                self.infodata.add_error_msg(f"Impossible de mettre plus de 20 caracteres pour {data_id}={self.data[data_id]}")
                log.error(self.infodata.get_last_msg())

    @ydt.fdebug
    def _check_ini_nir(self):
        data_id = "nir"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            if not ydt.check_valid_nir(self.data[data_id]):
                self.infodata.add_error_msg(f"La cle du {data_id.upper()} semble invalide pour {data_id}={self.data[data_id]}")
                log.error(self.infodata.get_last_msg())

    @ydt.fdebug
    def _check_ini_nom(self):
        data_id = "nom"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            # On verifie que data ne contient pas de chiffres
            if any(i.isdigit() for i in self.data[data_id]):
                self.infodata.add_error_msg(f"Chiffres interdits pour {data_id}={self.data[data_id]}")
                log.error(self.infodata.get_last_msg())
            # On verifie la longueur max
            if len(self.data[data_id]) > 32:
                self.infodata.add_error_msg(f"Impossible de mettre plus de 32 caracteres pour {data_id}={self.data[data_id]}")
                log.error(self.infodata.get_last_msg())

    @ydt.fdebug
    def _check_ini_siret(self):
        data_id = "siret"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            # On verifie que data est un entier
            try:
                int(self.data[data_id])
            except ValueError:
                self.infodata.add_error_msg(f"Le {data_id.upper()} ne doit contenir que des chiffres pour {data_id}={self.data[data_id]}")
                log.error(self.infodata.get_last_msg())
            # On verifie la longueur exacte
            if len(self.data_nir) != 14:
                self.infodata.add_error_msg(f"Le {data_id.upper()} doit faire exactement 14 caractères pour {data_id}={self.data[data_id]}")
                log.error(self.infodata.get_last_msg())

    @ydt.fdebug
    def _check_ini_finess_ps(self):
        data_id = "finess_ps"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            # On verifie que data est un entier
            try:
                int(self.data[data_id])
            except ValueError:
                self.infodata.add_error_msg(f"Le {data_id.upper()} ne doit contenir que des chiffres pour {data_id}={self.data[data_id]}")
                log.error(self.infodata.get_last_msg())
            # On verifie la longueur exacte
            if len(self.data[data_id]) != 9:
                self.infodata.add_error_msg(f"Le {data_id.upper()} doit faire exactement 9 caractères pour {data_id}={self.data[data_id]}")
                log.error(self.infodata.get_last_msg())

    @ydt.fdebug
    def _check_ini_date_evenement(self):
        data_id = "date_evenement"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            # On verifie que la date est valide
            try:
                datetime.datetime.strptime(self.data[data_id], "%Y%m%d")
            except ValueError:
                self.infodata.add_error_msg(f"Date incorrecte (format: AAAAMMJJ) pour {data_id}={self.data[data_id]}")
                log.error(self.infodata.get_last_msg())
            else:
                # On verifie que la date_evenement n'est pas superieure a la date du jour
                if datetime.datetime.strptime(self.data[data_id], "%Y%m%d") > datetime.datetime.now():
                    self.infodata.add_error_msg(f"Date superieure a la date du jour pour {data_id}={self.data[data_id]}")
                    log.error(self.infodata.get_last_msg())
                # On verifie que la date_evenement n'est pas superieure a la date_reception
                if datetime.datetime.strptime(self.data[data_id], "%Y%m%d") > datetime.datetime.strptime(self.data["date_reception"], "%Y%m%d"):
                    self.infodata.add_error_msg(f"Date superieure a la date de reception pour {data_id}={self.data[data_id]}")
                    log.error(self.infodata.get_last_msg())

    @ydt.fdebug
    def _check_ini_num_dossier(self):
        data_id = "num_dossier"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            # On verifie la longueur max
            if len(self.data_nom) > 30:
                self.infodata.add_error_msg(f"Impossible de mettre plus de 30 caracteres pour {data_id}={self.data[data_id]}")
                log.error(self.infodata.get_last_msg())

    @ydt.fdebug
    def _check_ini_commentaire(self):
        data_id = "commentaire"
        self.data[data_id] = self.ini_conf.get("general", data_id)

    @ydt.fdebug
    def _check_ini_attachments(self):
        # On verifie typedocX et fichierX
        # TODO : app_conf max_attachments_by_folder
        for i in range(0, 10):
            typedoc_id = "typedoc" + str(i)
            fichier_id = "fichier" + str(i)
            typedoc_vbool = self.addict_conf.getboolean("attachments_keys", typedoc_id)
            fichier_vbool = self.addict_conf.getboolean("attachments_keys", fichier_id)
            if typedoc_vbool and fichier_vbool:
                self.data[typedoc_id] = str.strip(self.ini_conf.get("fichiers", typedoc_id))
                self.data[fichier_id] = str.strip(self.ini_conf.get("fichiers", fichier_id))
                if (self.data[typedoc_id] != "" and self.data[fichier_id] == "") or (self.data[typedoc_id] == "" and self.data[fichier_id] != ""):
                    self.infodata.add_error_msg(f"Valeur obligatoire manquante pour le couple {typedoc_id}={self.data[typedoc_id]} / {fichier_id}={self.data[fichier_id]}")
                    log.error(self.infodata.get_last_msg())
                if self.data[typedoc_id] != "" and self.data[fichier_id] != "":
                    # Autres verifications sur typedocX
                    self._generic_check_ini_attachments_typedoc(typedoc_id, self.data[typedoc_id])
                    # Autres verifications sur fichierX
                    self._generic_check_ini_section_attachments_file(fichier_id, self.data[fichier_id])

    @ydt.fdebug
    def _generic_check_ini_attachments_typedoc(self, key, value):
        # On verifie que value ne contient pas de chiffres
        if any(i.isdigit() for i in value):
            self.infodata.add_error_msg(f"Chiffres interdits pour {key}={value}")
            log.error(self.infodata.get_last_msg())
        # On verifie que value ne contient pas d'espaces
        if " " in value:
            self.infodata.add_error_msg(f"Espaces interdits pour {key}={value}")
            log.error(self.infodata.get_last_msg())

    @ydt.fdebug
    def _generic_check_ini_section_attachments_file(self, key, value):
        file_path = os.path.join(self.folder_path, value)
        # On verifie que attachment a bien une extension valide
        if not value.endswith(ydt.get_ini_tuple(self.addict_conf.get("attachments", "extensions"))):
            self.infodata.add_error_msg(f"Extension incorrecte pour {key}={value}")
            log.error(self.infodata.get_last_msg())
        # On verifie que le fichier est bien existant
        if not os.path.exists(file_path):
            self.infodata.add_error_msg(f"Fichier inexistant pour {key}={value}")
            log.error(self.infodata.get_last_msg())
        # On verifie que le fichier a une taille inferieure ou egale a celle attendue
        elif os.path.getsize(file_path) > self.addict_conf.getint("attachments", "max_size"):
            self.infodata.add_error_msg(f"Poids du fichier trop lourd ({ydt.convert_filesize(os.path.getsize(file_path))}) pour {key}={value}")
            log.error(self.infodata.get_last_msg())
