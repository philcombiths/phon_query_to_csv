# -*- coding: utf-8 -*-
# TODO: Clean up logging.
# TODO Remove created temporary files.
# TODO Make ID of columns more of a generic function.
#   Else make robust to different filenames

"""
Three functions used in sequence, to batch process Phon query
output csv files in a directory or subdirectories.

Note: participant, phase, language, analysis variables  in gen_csv() must be
    modified to specify or extract values from the current data structure. 
    These values are usually extracted from the filename str or containing 
    directory name str (see lines 143-167).

Generates:
- 'AllPart_AllLang_AllAnalyses_data.csv' : All data, extracted only from the Phon file input
- 'data_accuracy.csv' : All data from above, with Accuracy, Deletion, Substitution data
- 'combined_dataset.csv': All data from above, with phone characteristic data and data from 'phono_error_patterns.py'
    
###
# Example use case:
directory = r"D:/Data/Spanish Tx Singletons - Copy"
res = gen_csv(directory)
file_path = merge_csv()
result = column_match(file_path)
###

Created on Thu Jul 30 18:18:01 2020
@modified: 2024-07-03
@author: Philip Combiths

"""
import logging

from phon_query_to_csv.logging_config import setup_logging
from phon_query_to_csv.gen_csv import gen_csv
from phon_query_to_csv.merge_csv import merge_csv
from phon_query_to_csv.calculate_accuracy import calculate_accuracy
from phon_query_to_csv.phone_data_expander import phone_data_expander
# from phon_query_to_csv.context_manager import enter_dir, change_dir
# from phon_query_to_csv.column_match import column_match # Optional

log = setup_logging(logging.INFO, __name__)

def phon_query_to_csv(directory, query, phase_re, participant_re,overwrite=False, target=True, actual=True):
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
    result = phone_data_expander(filepath, directory, target=False, actual=True)
    print("***** All processes complete. *****")
    return result

# Example use case:
if __name__ == "__main__":
    # parameters
    # directory = os.path.normpath(input("Enter directory: "))
    directory = "/Users/pcombiths/Documents/GitHub/phon_query_to_csv/tests/typology_actual_test"  # For testing
    #directory = r"C:\Users\pcombiths\Documents\GitHub\Phon_query_to_csv\tests\typology_actual_test" # For testing
    query = "Queries_v5_phone_listings_phrase.xml"  # Write keyword here
    overwrite=True
    print("**********************************\n")
    print("Available flavors:\n")
    print("    - tx")
    print("    - typology")
    print("    - new typology\n")
    # flavor = input("Specify flavor: ")
    flavor = "typology"  # For testing

    if flavor == "tx":
        participant_re = r"\w\d\d\d"
        phase_re = r"BL-\d{1,2}|Post-\dmo|Pre|Post|Mid|Tx-\d{1,2}"

    elif flavor == "typology":
        participant_re = r"\d\d\d"
        phase_re = r"p[IVX]+"

    elif flavor == "new typology":
        participant_re = r"\w{3,4}\d\d"
        phase_re = (
            r"no phases"  # No phases in this dataset. Trigger null regex result
        )

    output = phon_query_to_csv(directory, query, phase_re, participant_re, overwrite=overwrite, target=False)
    pass
