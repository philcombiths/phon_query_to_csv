# -*- coding: utf-8 -*-
"""
Simple script to make modifications to filenames in a directory.

Deprecated/single-use for completed project

Created on Thu Jul 30 18:51:18 2020
@author: Philip
"""

import os
from contextlib import contextmanager

@contextmanager
def change_dir(newdir):
    prevdir = os.getcwd()
    try:
        yield os.chdir(os.path.expanduser(newdir)) 
    finally:
        os.chdir(prevdir)

with change_dir("D:\Data\Spanish Tx Singletons"):
    for file in os.listdir("D:\Data\Spanish Tx Singletons"):
        if "EFE_A" in file:
            new_file = file.replace("EFE_A", "EFE-A")
            os.rename(file, new_file)
        if "EFE_B" in file:
            new_file = file.replace("EFE_B", "EFE-B")
            os.rename(file, new_file)
        if "(JZ Blind is for Mid probe)" in file:
            new_file = file.replace("(JZ Blind is for Mid probe)", "")
            os.rename(file, new_file)
    