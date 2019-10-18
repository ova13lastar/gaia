#!/bin/bash

# Bash script to build app using PyInstaller

# GLOBALS
scriptBaseName=gaia
now=$(date '+%Y%m%d-%H%M%S')
distPath=.builds/$now

# First check for PyInstaller
command -v pyinstaller >/dev/null 2>&1 || {
    echo >&2 "PyInstaller is required to build the executable.";
    echo >&2 "Please install PyInstaller with:";
    echo >&2 "pip install pyinstaller"
    exit 1;
}

# Cleanup before
echo ---------------------------------------
echo Nettoyage des anciens repertoires ...
rm -rf __pycache__
rm -rf .pytest_cache
rm -rf build

# PyInstaller
echo ---------------------------------------
echo Lancement de pyinstaller ...
pyinstaller --clean build.spec --distpath ./$distPath
# --upx-dir=/D/upx/

# Cleanup after
echo ---------------------------------------
echo Nettoyage final ...
rm -rf build

echo ---------------------------------------
echo Executable cree dans : $(pwd)/$distPath/$scriptBaseName/
