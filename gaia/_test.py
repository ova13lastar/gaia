from constants import *
import ydtools as ydt
from functools import wraps

# Initialisation du logger
log = ydt.init_logger()


class YD:

    def __init__(self):
        self.app_conf = ydt.load_ini_file(os.path.join('.', os.path.join(CONF_DIR_NAME, APP_CONF_FILE_NAME)))
        self.addict_conf = ydt.load_ini_file(os.path.join('.', os.path.join(CONF_DIR_NAME, self.app_conf["filenames"]["addict_conf"])))

    @ydt.fdebug
    def test(self, _param1):
        ydt.get_ini_tuple(self.addict_conf["general"]["processus"])
        ydt.get_ini_tuple(self.addict_conf["general"]["archivage"], "int")
        d = True
        return d


def main():
    # addict_config = init_addict_config()
    try:
        tab = [0, 1, 2, 3]
        yd = YD()
        yd.test("texte test")
    except Exception as e:
        log.exception(f"ERREUR INNATENDUE : {e}")


if __name__ == '__main__':
    main()
