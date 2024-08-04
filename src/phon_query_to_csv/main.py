# -*- coding: utf-8 -*-
# TODO: Clean up logging.
# TODO Remove created temporary files.
# TODO Make ID of columns more of a generic function.
#   Else make robust to different filenames

"""
Series of functions to batch process Phon analysis 
output csv files in a directory or subdirectories.

Note: participant, phase, language, analysis variables  in gen_csv() must be
    modified to specify or extract values from the current data structure. 
    These values are usually extracted from the filename str or containing 
    directory name str.

Generates:
- 'AllPart_AllLang_AllAnalyses_data.csv' : All data, extracted only from the Phon file input
- 'data_accuracy.csv' : All data from above, with Accuracy, Deletion, Substitution data
- 'full_accuracy_dataset.csv': All data from above, with phone characteristic data from 'ipa_features'

Created on Thu Jul 30 18:18:01 2020
@modified: 2024-07-05
@author: Philip Combiths

"""
import os
import logging

from phon_query_to_csv.logging_config import setup_logging
from phon_query_to_csv.gen_csv import gen_csv
from phon_query_to_csv.merge_csv import merge_csv
from phon_query_to_csv.calculate_accuracy import calculate_accuracy
from phon_query_to_csv.phone_data_expander import phone_data_expander
# from phon_query_to_csv.column_match import column_match # Optional

log = setup_logging(logging.INFO, __name__)

def phon_query_to_csv(directory, query, phase_re, participant_re, overwrite=False, target=True, actual=True):
    """
    Wrapper for sequence of functions.
    """
    # Note: filepath variable required within functions
    filepath = gen_csv(directory, query, phase_re, participant_re, overwrite=overwrite)
    filepath = (
        merge_csv(directory)
    )  # works with files created in previous step. No input needed.
    if target:
        filepath = calculate_accuracy(filepath)
    result = phone_data_expander(filepath, directory, target=target, actual=actual)
    print("***** All processes complete. *****")
    return result

# Example use case:
if __name__ == "__main__":
    # Default parameters
    directory = None
    query = None
    flavor = None
    overwrite = None
    target = None
    actual = None
    
    # Set Parameters Here:
    directory = "/Users/pcombiths/Library/CloudStorage/OneDrive-UniversityofIowa/CLD Lab/NCJC/data_analysis/prelim_IES_grant_2024/NWR Phon"
    query = "Queries_Target_v2"  # Write keyword here
    flavor = None  # For testing
    if 'flavor' not in locals() or flavor is None:
        print("\n**********************************\n")
        print("Available flavors:\n\ttx\n\ttypology\n\tnew typology\n\titold\n\tncjc\n")
        flavor = input("Specify flavor: ")
    
    if flavor == "tx":
        participant_re = r"\w\d\d\d"
        phase_re = r"BL-\d{1,2}|Post-\dmo|Pre|Post|Mid|Tx-\d{1,2}"
        target = True
        actual = True

    elif flavor == "typology":
        participant_re = r"\d\d\d"
        phase_re = r"p[IVX]+"
        target = False
        actual = True

    elif flavor == "new typology":
        participant_re = r"\w{3,4}\d\d"
        phase_re = r"no phases"  # No phases in this dataset. Trigger null regex result
        target = False
        actual = True
        
    elif flavor == "itold":
        participant_re = r"\w{4}\d{2}"
        phase_re = r"no phases"  # No phases in this dataset. Trigger null regex result
        target = True
        actual = True
        
    elif flavor == "ncjc":
        participant_re = r"\w{1}\d{3}"
        phase_re = r"Timepoint\d"
        target = True
        actual = True
        
    print("\n**********************************\n")
    print(f"Current parameters are:\ndirectory: {directory}\nquery: {query}\nflavor: {flavor}\ntarget: {target}\nactual: {actual}\noverwrite:{overwrite}")
    print("\n**********************************\n")
    input(f"Proceed? (y/n): ")
    output = phon_query_to_csv(directory, query, phase_re, participant_re, overwrite=False, target=target, actual=actual)
    pass
