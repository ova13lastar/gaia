#!/usr/bin/env python

import os
import sys
import subprocess


class Cpdf:

    def __init__(self):
        self.exe_path = os.path.abspath("./vendor/cpdf/cpdf.exe")

    def number_of_pages(self, infile_path):
        cmd = self.exe_path + " -pages " + os.path.normpath(infile_path)
        response = subprocess.run(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        try:
            return int(response.stdout.rstrip())
        except:
            return 0

    def squeeze(self, infile_path):
        cmd = self.exe_path + " -squeeze " + os.path.normpath(infile_path) + " -o " + os.path.normpath(infile_path)
        response = subprocess.run(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if response.returncode == 0:
            return True
        return False

    def split(self, infile_path, chunk=1):
        if (chunk < 1):
            print("Split impossible !")
            return False
        infile_basepath = os.path.dirname(infile_path)
        infile_name = os.path.splitext(os.path.basename(infile_path))[0]
        infile_ext = os.path.splitext(os.path.basename(infile_path))[1]
        outfile_path = os.path.join(infile_basepath, infile_name + "_%%%" + infile_ext)
        cmd = self.exe_path + " -split " + os.path.normpath(infile_path) + " 1 even -chunk " + str(chunk) + " -o " + os.path.normpath(outfile_path)
        response = subprocess.run(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if response.returncode == 0:
            return True
        return False


infile_path = "D:/Python_dev/gaia_src/20190710141628121_gemoba_ok/canon.pdf"
# file_out_path = "D:/Python_dev/gaia_src/20190710141628121_gemoba_ok/canon_squeeze.pdf"
cpdf = Cpdf()
# print(cpdf.squeeze(infile_path))

nb_pages_total = cpdf.number_of_pages(infile_path)
print(nb_pages_total)
nb_attachments = sum(1 for f in os.listdir(os.path.dirname(infile_path)) if not f.endswith("ini"))
print(nb_attachments)
# chunk = nb de pages par pdf : nb_pages_total / (nb_attachments_max - nb_attachments - fichier_en_cours) + 1
chunk = round(nb_pages_total / int(10 - nb_attachments - 1)+1)
print(chunk)
# print(chunk)
# print(cpdf.split(infile_path, chunk=chunk))
# print(cpdf.number_of_pages(infile_path))
