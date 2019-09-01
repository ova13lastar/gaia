import os
import sys
import logging
import logging.config

class App:
    # Nom de l'application
    __conf["APP_NAME"] = os.path.basename(os.getcwd()),
    # Libelle utilise pour une erreur fatale
    __conf["FATAL_ERROR"] = "ERREUR FATALE",
    # Extension utilisée pour le blocage
    __conf["LOCK_EXTENSION"] = ".lock",
    # Nom du dossier de configuration
    __conf["CONF_DIR_NAME"] = "conf",
    # Extension des fichiers de configuration
    __conf["CONF_FILE_EXTENSION"] = "ini"
    # Nom du fichier de configuration APP
    __conf["APP_CONF_FILE_NAME"] = "app" + "." + __conf["CONF_FILE_EXTENSION"]
    # Chemin du fichier de configuration APP
    __conf["APP_CONF_PATH"] = os.path.join(".", os.path.join(__conf["CONF_DIR_NAME"], __conf["APP_CONF_FILE_NAME"]))
    # Nom du fichier de configuration LOG
    __conf["LOG_CONF_FILE_NAME"] = "log" + "." + __conf["CONF_FILE_EXTENSION"]
    # Chemin du fichier de configuration APP
    __conf["LOG_CONF_PATH"] = os.path.join(".", os.path.join(__conf["CONF_DIR_NAME"], __conf["LOG_CONF_FILE_NAME"]))

    @staticmethod
    def config(name):
        return App.__conf[name]

# # Nom de l'application
# APP_NAME = os.path.basename(os.getcwd()),

# # -------------------------------
# # Constantes de configuration
# # -------------------------------

# # Nom du dossier de configuration
# CONF_DIR_NAME = "conf"

# # Extension des fichiers de configuration
# CONF_FILE_EXTENSION = "ini"

# # Nom du fichier de configuration APP
# APP_CONF_FILE_NAME = "app" + "." + CONF_FILE_EXTENSION
# # Chemin du fichier de configuration LOG
# APP_CONF_PATH = os.path.join(".", os.path.join(CONF_DIR_NAME, APP_CONF_FILE_NAME))

# # Nom du fichier de configuration LOG
# LOG_CONF_FILE_NAME = "log" + "." + CONF_FILE_EXTENSION
# # Chemin du fichier de configuration LOG
# LOG_CONF_PATH = os.path.join(".", os.path.join(CONF_DIR_NAME, LOG_CONF_FILE_NAME))

# # Nom du fichier de configuration ADDICT
# ADDICT_CONF_FILE_NAME = "addict" + "." + CONF_FILE_EXTENSION
# # Chemin du fichier de configuration ADDICT
# ADDICT_CONF_PATH = os.path.join(".", os.path.join(CONF_DIR_NAME, ADDICT_CONF_FILE_NAME))

# # Nom du fichier INFODATA
# INFODATA_FILE_NAME = "infodata" + "." + APP_NAME

# # -------------------------------
# # Autres constantes
# # -------------------------------

# # Libelle utilise pour une erreur fatale
# FATAL_ERROR = "ERREUR FATALE"

# # Extension utilisée pour le blocage
# LOCK_EXTENSION = ".lock"

# -------------------------------
# Logger
# -------------------------------


class ConfigLog:
    def __init__(self):
        """  Initialisation du logger

        Returns:
            dict: Objet log
        """
        try:
            self.log = logging.getLogger()
            logging.config.fileConfig(LOG_CONF_PATH, defaults={"logfilename": APP_NAME + ".log"})
        except Exception as e:
            print(f"{FATAL_ERROR} : lors de l'initialiation de la configuration {LOG_CONF_PATH}")
            print(f"{e}")
            # print(traceback.format_exc())
            sys.exit(1)

    def get_logger(self):
        return self.log

