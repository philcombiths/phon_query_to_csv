"""
For reading xls Phon query output files
"""
import os
import pandas as pd
from contextlib import contextmanager
import sys

@contextmanager
def change_dir(newdir):
    prevdir = os.getcwd()
    try:
        yield os.chdir(os.path.expanduser(newdir)) 
    finally:
        os.chdir(prevdir)
        print("Last directory used: ", newdir)
        print("Returned to directory: ", os.getcwd())

input_text = os.path.normpath(input('Enter text file path: '))
if len(input_text) == 1:
   input_text = os.path.normpath(r"C:\Users\Philip\csv_compiler_errors.txt")
    
def texttolist(input_text):
    with open(input_text, 'r') as f:
        x = f.read().splitlines()
        return x

folder_list = texttolist(input_text)

# for each file in list of files in directory xls_dir...

for folder in folder_list:
    if 'English' in folder:
        name = folder.split('\\')[-4]
        lang = 'English'

    else:
        name = folder.split('\\')[-3]
        lang = 'Spanish'

    phase = folder.split('\\')[-2]
    query = folder.split('\\')[-1]        

    for file in os.listdir(folder):
        if '.xls' in file:           
            with change_dir(folder):            
                # Read Excel file as dictionary of Pandas DataFrames (data_xls) Key = sheet name
                try:
                    data_xls = pd.read_excel(file, None)
                except IOError:
                    print(sys.exc_info()[1])
                    print('Unable to read {} {}'.format(file, type(file)))
                    print('{} skipped'.format(file))
                    break     
                print("Working in directory: ", os.getcwd())
                # Get list of sheets as xls_keys
                xls_keys = data_xls.keys()
                # For each sheet in file...
                for sheet in data_xls:
                    substring_list = ['Accurate', 'Deletions', 'Substitutions']
                    accuracy = sheet.split(';')[0]
                    if accuracy in substring_list:                                            
                        # Define working Excel tab as DataFrame
                        df_sheet = data_xls[sheet]
                        
                        df_sheet['Session'] = ''
                        df_sheet['Date'] = ''
                        df_sheet['Speaker'] = name
                        df_sheet['Age'] = ''
                        df_sheet['Group #'] = ''
                        df_sheet['Tier'] = ''
                        df_sheet['Range'] = ''
                        df_sheet['Result'] = ''
                        df_sheet['Session'] = ''
                        df_sheet['Query'] = ''
                        df_sheet['Analysis'] = ''
                        df_sheet['Phase'] = ''
                        df_sheet['Participant'] = name
                        df_sheet['Session'] = ''
                        df_sheet['Language'] = ''
                        df_sheet['Accuracy'] = ''
                        
                        df_sheet.filter(['Session', 'Date', 'Speaker', 'Age', 'Record #', 'Group #', 'Tier',
                            'Range', 'Result', 'IPA Target', 'IPA Actual', 'Orthography (Word)',
                            'IPA Target (Word)', 'IPA Actual (Word)', 'Target Stress (Word)',
                            'Actual Stress (Word)', 'Query', 'Analysis', 'Phase', 'Participant',
                            'Language', 'Accuracy'], axis = 1).to_csv('%s_%s_%s_%s_%s.csv' % (accuracy, name, lang, phase, query), 
                            encoding = 'utf-8', index = False)
                            
                        print(name,sheet, " Done")
                    else:
                        continue        
                    print('%s_%s_%s_%s_%s.csv' % (name, lang, phase, query, accuracy), "Done")
        else:
            continue
    print(folder, "Done")     
print("All files complete")