#!/usr/bin/env python

import os

# Nom de l'application
APP_NAME = os.path.basename(os.getcwd())

# -------------------------------
# CONSTANTES DE CONFIGURATION
# -------------------------------

# Nom du dossier de configuration
CONF_DIR_NAME = "conf"

# Extension des fichiers de configuration
CONF_FILE_EXTENSION = "ini"

# Nom du fichier de configuration APP
APP_CONF_FILE_NAME = "app" + "." + CONF_FILE_EXTENSION
# Chemin du fichier de configuration LOG
APP_CONF_PATH = os.path.join(".", os.path.join(CONF_DIR_NAME, APP_CONF_FILE_NAME))

# Nom du fichier de configuration LOG
LOG_CONF_FILE_NAME = "log" + "." + CONF_FILE_EXTENSION
# Chemin du fichier de configuration LOG
LOG_CONF_PATH = os.path.join(".", os.path.join(CONF_DIR_NAME, LOG_CONF_FILE_NAME))

# Nom du fichier de configuration ADDICT
ADDICT_CONF_FILE_NAME = "addict" + "." + CONF_FILE_EXTENSION
# Chemin du fichier de configuration ADDICT
ADDICT_CONF_PATH = os.path.join(".", os.path.join(CONF_DIR_NAME, ADDICT_CONF_FILE_NAME))

# Nom du fichier INFODATA
INFODATA_FILE_NAME = "infodata" + "." + APP_NAME

# -------------------------------
# Autres constantes
# -------------------------------

# Libelle utilise pour une erreur fatale
FATAL_ERROR = "ERREUR FATALE"

# Extension utilisée pour le blocage
LOCK_EXTENSION = ".lock"
