#!/usr/bin/env python

import os
import datetime
import logging

from constants import *
import ydtools as ydt

# Recuperation du logger
log = logging.getLogger()


class Addict:

    init_error = 0
    check_error = 0

    def __init__(self, folder_path, addict_conf=None):
        # Chargement de la configuration addict
        if addict_conf is None:
            try:
                self.addict_conf = ydt.load_ini_file(os.path.join('.', os.path.join(CONF_DIR_NAME, ADDICT_CONF_FILE_NAME)))
            except:
                self.init_error += 1
                return None
        else:
            self.addict_conf = addict_conf
        # On check le dossier a traiter et on se place dedans
        try:
            self.folder_path = folder_path
            log.debug(f"self.folder_path = {self.folder_path}")
            owd = os.getcwd()
            log.debug(f"Chemin courant (owd) = = {owd}")
            os.chdir(self.folder_path)
            log.debug(f"Chemin courant (getcwd) = {os.getcwd()}")
        except:
            self.init_error += 1
            os.chdir(owd)
            log.error(f"Dossier a traiter introuvable : {folder_path}")
        # On charge la configuration du fichier ini
        try:
            self.inifile_name = [f for f in os.listdir(self.folder_path) if f.endswith(self.addict_conf.get("ini", "extension"))][0]
            inifile_path = os.path.join(self.folder_path, self.inifile_name)
            self.ini_conf = ydt.load_ini_file(inifile_path)
        except:
            self.init_error += 1
            log.critical(f"Echec du chargement du fichier : {inifile_path}")
            return None
        finally:
            # Retour sur le directory initial pour eviter que le lock plante
            os.chdir(owd)
        # Initialisation des attributs de la classe
        try:
            # Dictionnaire des chemins des attachments
            self.attachments_paths = [os.path.abspath(f) for f in os.listdir(self.folder_path) if f.endswith(ydt.get_ini_tuple(self.addict_conf.get("attachments", "extensions")))]
            # Dictionnaire des data
            self.data = dict()
        except:
            log.critical(f"Echec de l'initialiation de la classe {__name__}")
            self.init_error += 1
            return None

    def get_inifile_path(self):
        return os.path.join(self.folder_path, self.inifile_name)

    def inject(self):
        log.info(f"!!!!!!!!!!!!!!!!!!!!!! INJECTION !!!!!!!!!!!!!!!!!!!!!")

    def check_ini(self):
        # On verifie la coherence des sections
        self._check_ini_sections()
        # On verifie les keys/values dans chaque section
        if self.check_error == 0:
            # On verifie la section [general]
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
            # On verifie la section [attachments]
            self._check_ini_attachments_typedoc0()
            self._check_ini_attachments_fichier0()
            self._check_ini_attachments_others()
        # On renvoie un bool comme resultat
        log.debug(f"self.check_error = {self.check_error}")
        if self.check_error == 0:
            return True
        return False

    def check_attachments(self):
        return True

    def _check_ini_sections(self):
        # On verifie que ini_conf contient qque chose
        if not self.ini_conf:
            log.error(f"Fichier INI de configuration vide ou mal charge : {self.get_inifile_path()}")
            self.check_error += 1
            return False
        # On verifie que les sections existent bien
        for s in ydt.get_ini_tuple(self.addict_conf.get("ini", "sections")):
            if not self.ini_conf.has_section(s):
                log.error(f"Section inexistante : {s}")
                self.check_error += 1
                return False
        for k, v in self.addict_conf.items("general_keys"):
            # On verifie que les cles de la section [general] existent bien
            if not self.ini_conf.has_option("general", k):
                log.error(f"Cle inexistante : {k}=")
                self.check_error += 1
            # On verifie que les valeurs obligatoires de la section [general] sont bien renseignees
            vbool = self.addict_conf.getboolean("general_keys", k)
            if vbool and self.ini_conf.get("general", k) == "":
                log.error(f"Valeur obligatoire manquante pour la cle : {k}=")
                self.check_error += 1

    def _check_ini_processus(self):
        data_id = "processus"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        # On verifie que les cles sont renseignes pour les processus particuliers (regles metiers)
        if self.data[data_id] not in self.addict_conf.items("general_processus_key_rules") and \
                self.ini_conf.get("general", "nir") == "" and \
                self.ini_conf.get("general", "nom") == "":
            log.error(f"Valeur obligatoire manquante les cles nir= et nom= alors que {data_id}={self.data[data_id]}")
            self.check_error += 1
        # On verifie que le processus correspond a un processus valide
        if self.data[data_id] not in ydt.get_ini_tuple(self.addict_conf.get("general", data_id)):
            log.error(f"Valeur incorrecte : {data_id}={self.data[data_id]}")
            self.check_error += 1

    def _check_ini_archivage(self):
        data_id = "archivage"
        self.data[data_id] = int(str.strip(self.ini_conf.get("general", data_id)))
        if self.data[data_id] not in ydt.get_ini_tuple(self.addict_conf.get("general", data_id), "int"):
            log.error(f"Valeur incorrecte pour {data_id}={self.data[data_id]}")
            self.check_error += 1

    def _check_ini_date_reception(self):
        data_id = "date_reception"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            # On verifie que la date est valide
            try:
                datetime.datetime.strptime(self.data[data_id], "%Y%m%d")
            except ValueError:
                log.error(f"Date incorrecte (format: AAAAMMJJ) pour {data_id}={self.data[data_id]}")
                self.check_error += 1
            else:
                # On verifie que la date n'est pas superieure a la date du jour
                if datetime.datetime.strptime(self.data[data_id], "%Y%m%d") > datetime.datetime.now():
                    log.error(f"Date superieure a la date du jour pour {data_id}={self.data[data_id]}")
                    self.check_error += 1

    def _check_ini_index_metier(self):
        data_id = "index_metier"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            # On verifie la longueur max
            if len(self.data[data_id]) > 20:
                log.error(f"Impossible de mettre plus de 20 caracteres pour {data_id}={self.data[data_id]}")
                self.check_error += 1

    def _check_ini_nir(self):
        data_id = "nir"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            if not ydt.check_valid_nir(self.data[data_id]):
                log.error(f"La cle du {data_id.upper()} semble invalide pour {data_id}={self.data[data_id]}")
                self.check_error += 1

    def _check_ini_nom(self):
        data_id = "nom"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            # On verifie que data ne contient pas de chiffres
            if any(i.isdigit() for i in self.data[data_id]):
                log.error(f"Chiffres interdits pour {data_id}={self.data[data_id]}")
                self.check_error += 1
            # On verifie la longueur max
            if len(self.data[data_id]) > 32:
                log.error(f"Impossible de mettre plus de 32 caracteres pour {data_id}={self.data[data_id]}")
                self.check_error += 1

    def _check_ini_siret(self):
        data_id = "siret"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            # On verifie que data est un entier
            try:
                int(self.data[data_id])
            except ValueError:
                log.error(f"Le {data_id.upper()} ne doit contenir que des chiffres pour {data_id}={self.data[data_id]}")
                self.check_error += 1
            # On verifie la longueur exacte
            if len(self.data_nir) != 14:
                log.error(f"Le {data_id.upper()} doit faire exactement 14 caractères pour {data_id}={self.data[data_id]}")
                self.check_error += 1

    def _check_ini_finess_ps(self):
        data_id = "finess_ps"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            # On verifie que data est un entier
            try:
                int(self.data[data_id])
            except ValueError:
                log.error(f"Le {data_id.upper()} ne doit contenir que des chiffres pour {data_id}={self.data[data_id]}")
                self.check_error += 1
            # On verifie la longueur exacte
            if len(self.data[data_id]) != 9:
                log.error(f"Le {data_id.upper()} doit faire exactement 9 caractères pour {data_id}={self.data[data_id]}")
                self.check_error += 1

    def _check_ini_date_evenement(self):
        data_id = "date_evenement"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            # On verifie que la date est valide
            try:
                datetime.datetime.strptime(self.data[data_id], "%Y%m%d")
            except ValueError:
                log.error(f"Date incorrecte (format: AAAAMMJJ) pour {data_id}={self.data[data_id]}")
                self.check_error += 1
            else:
                # On verifie que la date_evenement n'est pas superieure a la date du jour
                if datetime.datetime.strptime(self.data[data_id], "%Y%m%d") > datetime.datetime.now():
                    log.error(f"Date superieure a la date du jour pour {data_id}={self.data[data_id]}")
                    self.check_error += 1
                # On verifie que la date_evenement n'est pas superieure a la date_reception
                if datetime.datetime.strptime(self.data[data_id], "%Y%m%d") > datetime.datetime.strptime(self.data["date_reception"], "%Y%m%d"):
                    log.error(f"Date superieure a la date de reception pour {data_id}={self.data[data_id]}")
                    self.check_error += 1

    def _check_ini_num_dossier(self):
        data_id = "num_dossier"
        self.data[data_id] = str.strip(self.ini_conf.get("general", data_id))
        if self.data[data_id] != "":
            # On verifie la longueur max
            if len(self.data_nom) > 30:
                log.error(f"Impossible de mettre plus de 30 caracteres pour {data_id}={self.data[data_id]}")
                self.check_error += 1

    def _check_ini_commentaire(self):
        data_id = "commentaire"
        self.data[data_id] = self.ini_conf.get("general", data_id)

    def _check_ini_attachments_typedoc0(self):
        data_id = "typedoc0"
        self.data[data_id] = str.strip(self.ini_conf.get("fichiers", data_id))
        # Obligatoire
        if self.data[data_id] == "":
            log.error(f"Valeur obligatoire manquante pour {data_id}={self.data[data_id]}")
            self.check_error += 1
        # Autres verifications
        self._generic_check_ini_attachments_typedoc(data_id, self.data[data_id])

    def _check_ini_attachments_fichier0(self):
        data_id = "fichier0"
        self.data[data_id] = str.strip(self.ini_conf.get("fichiers", data_id))
        # Obligatoire
        if self.data[data_id] == "":
            log.error(f"Valeur obligatoire manquante pour {data_id}={self.data[data_id]}")
            self.check_error += 1
        # Autres verifications
        self._generic_check_ini_section_attachments_file(data_id, self.data[data_id])

    def _check_ini_attachments_others(self):
        # On verifie typedocX et fichierX
        for i in range(1, 10):
            typedoc_id = "typedoc" + str(i)
            fichier_id = "fichier" + str(i)
            self.data[typedoc_id] = str.strip(self.ini_conf.get("fichiers", typedoc_id))
            self.data[fichier_id] = str.strip(self.ini_conf.get("fichiers", fichier_id))
            if (self.data[typedoc_id] != "" and self.data[fichier_id] == "") or (self.data[typedoc_id] == "" and self.data[fichier_id] != ""):
                log.error(f"Valeur obligatoire manquante pour le couple {typedoc_id}={self.data[typedoc_id]} / {fichier_id}={self.data[fichier_id]}")
                self.check_error += 1
            if self.data[typedoc_id] != "" and self.data[fichier_id] != "":
                # Autres verifications sur typedocX
                self._generic_check_ini_attachments_typedoc(typedoc_id, self.data[typedoc_id])
                # Autres verifications sur fichierX
                self._generic_check_ini_section_attachments_file(fichier_id, self.data[fichier_id])

    @ydt.fdebug
    def _generic_check_ini_attachments_typedoc(self, key, value):
        # On verifie que value ne contient pas de chiffres
        if any(i.isdigit() for i in value):
            log.error(f"Chiffres interdits pour {key}={value}")
            self.check_error += 1
        # On verifie que value ne contient pas d'espaces
        if " " in value:
            log.error(f"Espaces interdits pour {key}={value}")
            self.check_error += 1

    @ydt.fdebug
    def _generic_check_ini_section_attachments_file(self, key, value):
        file_path = os.path.join(self.folder_path, value)
        # On verifie que attachment a bien une extension valide
        if not value.endswith(ydt.get_ini_tuple(self.addict_conf.get("attachments", "extensions"))):
            log.error(f"Extension incorrecte pour {key}={value}")
            self.check_error += 1
        # On verifie que le fichier est bien existant
        if not os.path.exists(file_path):
            log.error(f"Fichier inexistant pour {key}={value}")
            self.check_error += 1
        # On verifie que le fichier a une taille inferieure ou egale a celle attendue
        if os.path.getsize(file_path) > self.addict_conf.getint("attachments", "max_size"):
            log.error(f"Poids du fichier trop lourd ({ydt.convert_filesize(os.path.getsize(file_path))}) pour {key}={value}")
            self.check_error += 1
