# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 17:54:46 2020

@author: Philip
"""

# -*- coding: utf-8 -*-
## Set KEYWORD Column in lines 64-67

# -*- coding: utf-8 -*-
# Python 3
### Edit directory of csv output files from a Phones query in Phon, Saves to same directory. 
### Compile every item in "Accurate", "Deleted", and "Substitutions" files into a single master file.


# Preliminaries
import pandas as pd
import os
import io
import shutil
import glob
import csv
import sys
import logging
from contextlib import contextmanager

# Use log for debugging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(message)s - %(levelname)s - %(asctime)s')
formatter2 = logging.Formatter('%(message)s')
#Prevent duplicate logs
if (log.hasHandlers()):
    log.handlers.clear()

fh = logging.FileHandler('csv_compiler_errors.txt')
fh.setLevel(logging.CRITICAL)
fh.setFormatter(formatter2)
log.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
log.addHandler(ch)


# Create contextmanager function that changes directory using with then returns to original directory on completion
@contextmanager
def change_dir(newdir):
    prevdir = os.getcwd()
    try:
        yield os.chdir(os.path.expanduser(newdir)) 
    finally:
        os.chdir(prevdir)
        print("Last directory used: ", newdir)
        print("Returned to directory: ", os.getcwd())

# User input base directory path
directory = os.path.normpath(input('Enter CSV directory path: '))

## Walk through directories, stopping at certain folders to run processes
with change_dir(os.path.normpath(directory)):
    log.info('Working in %s' % os.getcwd())
    for index, (dirName, subdirList, fileList) in enumerate(os.walk(os.getcwd())):
        # log.info(dirName)
        # for fname in fileList:
        #     log.info('\t%s' % fname)
        # Only enter participant folders that begin with "S" 
        if index == 0:
            # log.info(subdirList)
            for item in subdirList:
                if not item.startswith('S'):
                    subdirList.remove(item)
                    log.info('%s skipped' % item)
            # log.info(subdirList)
        if 'Consonant Accuracy' in dirName:
            
            ## Check for Excel files in directory
            if any(fname.endswith('.xls') for fname in os.listdir(dirName)):
                log.warning('**Excel files located in this directory:')
                log.warning(dirName)
                log.critical(dirName)
            if any(fname.endswith('.xlsx') for fname in os.listdir(dirName)):
                log.warning('**Excel files located in this directory:')
                log.warning(dirName)
                log.critical(dirName)
            ## Check for CSV files in directory
            if not any(fname.endswith('.csv') for fname in os.listdir(dirName)):
                log.warning('**No .csv files located in this directory:')
                log.warning(dirName)
                # raise Exception('Likely empty folder encountered')
                # Could also go back to prior steps and enter a different folder?
            
            log.info('extracting from %s' %dirName)
            try:
                os.makedirs(os.path.join(directory, 'Compiled Data'))
            except WindowsError:
                log.warning(sys.exc_info()[1])
                log.warning('Compiled Data directory already created.')
            
                
            for cur_csv in os.listdir(dirName):
                # Skip other files (listed below) if they occurr
                if cur_csv == 'desktop.ini':
                    print (cur_csv, ' skipped')
                    continue
                if cur_csv == 'Report Template.txt':
                    print (cur_csv, ' skipped')
                    continue
                if cur_csv == 'Report.html':
                    print (cur_csv, ' skipped')
                    continue
                if 'Summary' in cur_csv:
                    print (cur_csv, ' skipped')
                    continue    
                        
                # Include only CSV files
                if cur_csv.endswith('.csv'):
                    # Only works with "Accurate", "Deleted", and "Substitutions" files
                    substring_list = ['Accurate', 'Deleted', 'Deletions', 'Substitutions']
                    if any(substring in cur_csv for substring in substring_list):                
                        # open CSV file in read mode with UTF-8 encoding
                        with io.open(os.path.join(dirName, cur_csv), mode='r', encoding='utf-8') as current_csv:
                            # create pandas DataFrame df from csv file
                            df = pd.read_csv(current_csv, encoding='utf-8')
                            
                            # Add keyword column
                            keyword = 'Consonant Accuracy Phon 2.2b21 wDiacritics' # Write keyword here
                            label = 'Query' # Write column label for keyword here
                            df[label] = keyword
        
                            analysis = dirName.split('\\')[-1]
                            df['Analysis'] = dirName.split('\\')[-1]
                            phase = dirName.split('\\')[-2]
                            df['Phase'] = dirName.split('\\')[-2]                            
                            if dirName.split('\\')[-3] == 'English':
                                participant = dirName.split('\\')[-4]
                                df['Participant'] = dirName.split('\\')[-4]
                                language = 'English'
                                df['Language'] = 'English'
                            else:
                                participant = dirName.split('\\')[-3]
                                df['Participant'] = dirName.split('\\')[-3]
                                language = 'Spanish'
                                df['Language'] = 'Spanish'                     
                   
                            # Add column of Speaker ID extracted from filename
                            df['Speaker'] = cur_csv.split('_')[1].split('.')[0]
                            
                            # Add column of source csv query type, extracted from filename
                            accuracy = cur_csv.split('_')[0].split('.')[0]
                            if accuracy == 'Deletions':
                                accuracy = 'Deleted'
                            df['Accuracy'] = accuracy

                            print ('***********************************************\n', list(df))
        
                            # Save REV_csv 
                            # With UTF-8 BOM encoding for Excel readability
                            

                            log.info('Current working directory'+os.getcwd())
                            try:
                                df.to_csv(os.path.join(directory,'Compiled Data', '%s_%s_%s_%s_%s.csv' % (participant, language, phase, analysis, accuracy)), encoding = 'utf-8-sig', index=False)
                            except FileNotFoundError:
                                log.error(sys.exc_info()[1])
                                log.error('Compiled Data folder not yet created')

                            ### After one session is compiled, add to other sessions for that participant
                            
            ## THIS NEEDS TO HAPPEN AFTER COMPILING ALL FILES FOR THAT PARTICIPANT                
                            
            ## Merge revised csvs into a single master csv file

            try:
                os.makedirs(os.path.join(directory, 'Compiled Data', 'Full'))
            except WindowsError:
                log.warning(sys.exc_info()[1])
                log.warning('Compiled Data directory already created.')
            
            with io.open(os.path.join(directory, 'Compiled Data','Full', '%s.csv' % (participant)), 'wb') as outfile:
                log.info(outfile)
                # participantdata = os.path.join(directory, 'Compiled Data', '%s*.csv' (participant))
                for i, fname in enumerate(glob.glob(directory + r"\\Compiled Data\\" + participant + "*.csv")):      

                    with io.open(fname, 'rb') as infile:
                        if i != 0:
                            infile.readline()  # Throw away header on all but first file
                        # Block copy rest of file from input to output without parsing
                        shutil.copyfileobj(infile, outfile)
                        log.info(fname + " has been imported.")
                csv.writer(outfile)
                log.info('Saved', outfile)
                
