# -*- coding: utf-8 -*-
# TODO: Incorporate an Error Score column
# TODO: Clean up logging.
# TODO: Remove created temporary files.
# TODO: Make ID of columns more of a generic function.
#           Else make robust to different filenames
# TODO: Potentially fix Probe Type and Probe columns. 

"""
Series of functions to batch process Phon analysis 
output csv files in a directory or subdirectories.

Generates:
- 'AllPart_AllLang_AllAnalyses_data.csv' : All data extracted from Phon csv input
- 'data_accuracy.csv' : All data from above, plus Accuracy, Deletion, Substitution data
- 'full_accuracy_dataset.csv': All data from above, plus phone characteristics from ipa_features.py

Created on Thu Jul 30 18:18:01 2020
@modified: 2025-07-25
@author: Philip Combiths
@contributors: Francesco Vial
"""

import logging

from phon_query_to_csv.logging_config import setup_logging
from phon_query_to_csv.gen_csv import gen_csv
from phon_query_to_csv.merge_csv import merge_csv
from phon_query_to_csv.calculate_accuracy import calculate_accuracy
from phon_query_to_csv.phone_data_expander import phone_data_expander
from phon_query_to_csv.create_pivot_table import create_pivot_table
# from phon_query_to_csv.column_match import column_match # Optional

log = setup_logging(logging.INFO, __name__)

def phon_query_to_csv(directory, query, phase_re, participant_re, overwrite=False, target=True, actual=True):
    """
    Wrapper for sequence of functions.
    """
    # Note: filepath variable required within functions
    gen_csv_result = gen_csv(directory, query, phase_re, participant_re, overwrite=overwrite)
    filepath = merge_csv(gen_csv_result[0])
    if target:
        filepath = calculate_accuracy(filepath)
    result = phone_data_expander(filepath, gen_csv_result[0], target=target, actual=actual)
    print("***** full_annotated_dataset.csv generated successfully. *****\n")
    result = create_pivot_table(gen_csv_result[0])
    print("***** pivot_table_dataset.csv generated successfully. *****\n")
    return result

# Interactive Module Execution
if __name__ == "__main__":
    # Default parameters
    directory = None
    query = None
    flavor = None
    overwrite = False
    target = True
    actual = True

    # Set Parameters Here:
    directory = None
    query = "Queries_Target_v2"  # Write query name here: e.g., "Queries_Target_v2", "Queries_Actual_v2"
    flavor = None  # Specify flavor (see options below)

    if 'flavor' not in locals() or flavor is None:
        print("\n**********************************\n")
        print("Available flavors:\n\ttx\n\ttypology\n\tnew typology\n\titold\n\tncjc\n\tcustom\n")
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
        participant_re = r"\w{1}\d{4}"
        phase_re = r"Timepoint\d|Pre|Post|Fall|Spring|Winter|Summer"
        target = True
        actual = True

    elif flavor == "custom":
        participant_re = input("Enter participant regex: ")
        phase_re = input("Enter phase regex: ")
        target = input("Target? (y/n): ").lower() == 'y'
        actual = input("Actual? (y/n): ").lower() == 'y'

    print("\n**********************************\n")
    print("Current parameters are:\n-----------------------")
    print(f"directory: {directory}\nquery: {query}\nflavor: {flavor}\ntarget: {target}\nactual: {actual}\noverwrite:{overwrite}")
    print("\n**********************************\n")
    input("Proceed? (y/n): ")
    
    # Execute function
    output = phon_query_to_csv(
        directory=directory, 
        query=query, 
        phase_re=phase_re, 
        participant_re=participant_re,
        overwrite=overwrite, 
        target=target, 
        actual=actual
    )
