#!/usr/bin/env python

from constants import *
import ydtools
import gaia as gaia_
import addict

# Initialisation du logger
log = ydtools.init_logger()


def main():
    log.info("-------------------------------------------------")
    log.info(f"-- DEMARRAGE DE L'APPLICATION : {APP_NAME.upper()}")
    log.info("-------------------------------------------------")
    try:
        gaia = gaia_.Gaia()
        gaia.scan_root_path()
    except Exception as e:
        log.exception(f"ERREUR INNATENDUE : {e}")


if __name__ == '__main__':
    main()
