#!/usr/bin/env python

import os

# Nom de l'application
APP_NAME = os.path.basename(os.getcwd())

# -------------------------------
# CONSTANTES DE CONFIGURATION
# -------------------------------

# Nom du dossier de configuration
CONF_DIR_NAME = "conf"

# Nom du fichier de configuration APP
APP_CONF_FILE_NAME = "app.ini"
# Chemin du fichier de configuration LOG
APP_CONF_PATH = os.path.join(".", os.path.join(CONF_DIR_NAME, APP_CONF_FILE_NAME))

# Nom du fichier de configuration LOG
LOG_CONF_FILE_NAME = "log.ini"
# Chemin du fichier de configuration LOG
LOG_CONF_PATH = os.path.join(".", os.path.join(CONF_DIR_NAME, LOG_CONF_FILE_NAME))

# Nom du fichier de configuration ADDICT
ADDICT_CONF_FILE_NAME = "addict.ini"
# Chemin du fichier de configuration ADDICT
ADDICT_CONF_PATH = os.path.join(".", os.path.join(CONF_DIR_NAME, ADDICT_CONF_FILE_NAME))

# -------------------------------
# Autres constantes
# -------------------------------

# Libelle utilise pour une erreur fatale
FATAL_ERROR = "ERREUR FATALE"

# Extension utilisée pour le blocage
LOCK_EXTENSION = ".lock"
