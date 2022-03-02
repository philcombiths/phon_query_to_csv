# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 16:26:17 2020

@author: Philip

Simple code to merge multiple CSVs in a directory into a single file. 
Must have same header structure.

"""
import os
import csv
import io
import shutil
from contextlib import contextmanager

@contextmanager
def enter_dir(newdir):
    prevdir = os.getcwd()
    try:
        yield os.chdir(newdir) 
    finally:
        os.chdir(prevdir)
        
        
@contextmanager
def change_dir(newdir):
    prevdir = os.getcwd()
    try:
        yield os.chdir(os.path.expanduser(newdir)) 
    finally:
        os.chdir(prevdir)

direct = r"D:\Montreal Forced Aligner\mfa\s104\Words"
outfile = r"merged.csv"

with change_dir(direct):         
    with io.open(r"merged.csv", 'wb') as outfile:
        for i, fname in enumerate(os.listdir()):    
            print(outfile)
            with io.open(fname, 'rb') as infile:
                if i != 0:
                    infile.readline()  # Throw away header on all but first file
                # Block copy rest of file from input to output without parsing
                shutil.copyfileobj(infile, outfile)
                print(fname + " has been imported.")                            
        csv.writer(outfile)