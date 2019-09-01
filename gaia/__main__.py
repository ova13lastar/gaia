#!/usr/bin/env python

# from constants import *
# import ydtools as ydt
import config
import gaianew as g
# import addict

# # Initialisation du logger
# log = ydt.init_logger()


def main():
    # config.ConfigLog()
    # log = ConfigLog.get_logger()
    try:
        gaia = g.Gaia()
    except Exception as e:
        log.exception(f"ERREUR INNATENDUE : {e}")

# def main():
#     log.info("-------------------------------------------------")
#     log.info(f"-- DEMARRAGE DE L'APPLICATION : {APP_NAME.upper()}")
#     log.info("-------------------------------------------------")
#     try:
#         gaia = g.Gaia()
#         gaia.check_infodata()
#         # print(gaia.get_app_conf())
#         # gaia.scan_root_path()
#     except Exception as e:
#         log.exception(f"ERREUR INNATENDUE : {e}")


if __name__ == '__main__':
    main()
