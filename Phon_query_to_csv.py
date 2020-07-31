# -*- coding: utf-8 -*-
"""
Two functions, intended to be used in sequence, to batch process Phon query
output csv files in a directory or subdirectories.

Note: participant, phase, language, analysis variables should be modified to
    extract values from the current data structure. These values are usually
    extracted from the filenames or their containing directory (see lines 114-139)


#Example use case:
directory = "D:\Data\Spanish Tx Singletons"
res = gen_csv(directory)
merge_csv(separate_participants=True, participant_list=res[0])


Created on Thu Jul 30 18:18:01 2020
@author: Philip
"""
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
import regex as re

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

def gen_csv(directory):
    participant_list = []
    phase_list = []
    language_list = []
    analysis_list = []
    file_count = 0
    assert 'Compiled' not in os.listdir(directory), "Compiled directory already exists. Move or remove before executing script,"
    with change_dir(os.path.normpath(directory)):
        for dirName, subdirList, fileList in os.walk(os.getcwd()):
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
            log.info('extracting from %s' %dirName)
            try:
                os.makedirs(os.path.join(directory, 'Compiled', 'uniform_files'))
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
                        file_count += 1
                        with io.open(os.path.join(dirName, cur_csv), mode='r', encoding='utf-8') as current_csv:
                            # create pandas DataFrame df from csv file
                            df = pd.read_csv(current_csv, encoding='utf-8')                            
                            ###################################################
                            #### Extract keyword and column values
                            keyword = 'Consonant Accuracy Phon 2.2b21 wDiacritics' # Write keyword here
                            label = 'Query' # Write column label for keyword here
                            df[label] = keyword        
                            analysis = "Singleton Accuracy"
                            analysis_list.append(analysis)
                            df['Analysis'] = analysis
                            #if re.match("BL\d|\d-MoPost|Pre|Post|Mid", cur_csv).group(0)
                            phase = re.findall(r"BL\d|\d-MoPost|Pre|Post|Mid", cur_csv)[0]
                            phase_list.append(phase)
                            df['Phase'] = phase  
                            language = 'Spanish'
                            language_list.append(language)
                            df['Language'] = language
                            participant = cur_csv.split('_')[1]
                            participant_list.append(participant)
                            df['Participant'] = participant
                            # Add column of Speaker ID extracted from filename
                            df['Speaker'] = participant                            
                            # Add column of source csv query type, extracted from filename
                            accuracy = cur_csv.split('_')[0].split('.')[0]
                            if accuracy == 'Deletions':
                                accuracy = 'Deleted'
                            df['Accuracy'] = accuracy
                            ###################################################
                            print ('***********************************************\n', list(df))
                            
                            # Save REV_csv 
                            # With UTF-8 BOM encoding for Excel readability
                            log.info('Current working directory'+os.getcwd())
                            try:
                                df.to_csv(os.path.join(directory,'Compiled', 'uniform_files', '%s_%s_%s_%s_%s.csv' % (participant, language, phase, analysis, accuracy)), encoding = 'utf-8-sig', index=False)
                            except FileNotFoundError:
                                log.error(sys.exc_info()[1])
                                log.error('Compiled Data folder not yet created')
        return (set(participant_list), set(phase_list), set(language_list), set(analysis_list), file_count)

def merge_csv(participant_list=['AllPart'], language_list=['AllLang'], 
              analysis_list=['AllAnalyses'], separate_participants=False, 
              separate_languages=False, separate_analyses=False):
    try:
        os.makedirs(os.path.join(directory, 'Compiled', 'merged_files'))
    except WindowsError:
        log.warning(sys.exc_info()[1])
        log.warning('Compiled Data directory already created.')        
    for participant in participant_list:
        for language in language_list:
            for analysis in analysis_list:
                with io.open(os.path.join(directory, 'Compiled','merged_files', 
                                          f'{participant}_{language}_{analysis}_data.csv'), 'wb') as outfile:
                    log.info(outfile)
                    # participantdata = os.path.join(directory, 'Compiled Data', '%s*.csv' (participant))            
                    if separate_participants:
                        if separate_languages:
                            if separate_analyses:
                                file_search_term = f"{directory}\\Compiled\\uniform_files\\*{participant}*{language}*{analysis}*.csv"
                            else:
                                file_search_term = f"{directory}\\Compiled\\uniform_files\\*{participant}*{language}*.csv"
                        else:
                            if separate_analyses:
                                file_search_term = f"{directory}\\Compiled\\uniform_files\\*{participant}*{analysis}*.csv"
                            else:
                                file_search_term = f"{directory}\\Compiled\\uniform_files\\*{participant}*.csv"                       
                    else:
                        if separate_languages:
                            if separate_analyses:
                                file_search_term = f"{directory}\\Compiled\\uniform_files\\*{language}*{analysis}*.csv"
                            else:
                                file_search_term = f"{directory}\\Compiled\\uniform_files\\*{language}*.csv"
                        else:
                            if separate_analyses:
                                file_search_term = f"{directory}\\Compiled\\uniform_files\\*{analysis}*.csv"
                            else:
                                file_search_term = f"{directory}\\Compiled\\uniform_files\\*.csv"
                    for i, fname in enumerate(glob.glob(file_search_term)):      
                        with io.open(fname, 'rb') as infile:
                            if i != 0:
                                infile.readline()  # Throw away header on all but first file
                            # Block copy rest of file from input to output without parsing
                            shutil.copyfileobj(infile, outfile)
                            log.info(fname + " has been imported.")                            
                    csv.writer(outfile)
                    log.info('Saved', outfile)        
             
"""
#Example use case:
    
directory = "D:\Data\Spanish Tx Singletons"
res = gen_csv(directory)
merge_csv(separate_participants=True, participant_list=res[0])
"""
            