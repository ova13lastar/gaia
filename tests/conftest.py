# import pprint
import os
import sys

# Insertion du GAIA_PATH dans le PYTHONPATH
GAIA_PATH = os.path.normpath(os.path.join(os.path.join(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')), "src"), "gaia"))
sys.path.insert(0, GAIA_PATH)
# Suppression des fichiers de logs
LOGS_PATH = os.path.normpath(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), "logs"))
for f in os.listdir(LOGS_PATH):
    os.remove(os.path.join(LOGS_PATH, f))
# Chemin des fixtures
FIXTURES_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), 'fixtures'))
