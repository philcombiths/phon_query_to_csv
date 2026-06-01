# -*- coding: utf-8 -*-
# TODO: Incorporate an Error Score column
# TODO: Clean up logging.
# TODO: Remove created temporary files.
# TODO: Make ID of columns more of a generic function.
#           Else make robust to different filenames
# TODO: Potentially fix Probe Type and Probe columns.
# TODO: Package source code as an executable

"""
Series of functions to batch process Phon analysis 
output csv files in a directory or subdirectories.

Generates:
- 'AllPart_AllLang_AllAnalyses_data.csv' : All data extracted from Phon csv input
- 'data_accuracy.csv' : All data from above, plus Accuracy, Deletion, Substitution data
- 'full_annotated_dataset.csv': All data from above, plus phone characteristics from ipa_features.py
- 'pivot_table_dataset.csv': All data from above, formatted into a pivot table

Created on Thu Jul 30 18:18:01 2020
@modified: 2026-05-15
@author: Philip Combiths
@contributors: Francesco Vial
"""

import logging

from phon_query_to_csv.logging_config import setup_logging
from phon_query_to_csv.visualize_query import visualize_query

log = setup_logging(logging.INFO, __name__)

def phon_query_to_csv(
        label, 
        path, 
        flavor, 
        phase_re, 
        participant_re, 
        target, 
        actual, 
        blanking
):
    """
    Run a query on CSV data taken from Phon
    
    Parameters:
    -----------
    label : str
        Label for query identification
    path : str
        Directory path containing the data files
    flavor : str
        Name of the flavor of analysis
    phase_re : str
        Regex for phase identification
    participant_re : str
        Regex for participant identification
    target : bool
        Whether to analyze targets
        If True, analyze targets
        If False, ignore targets
    actual : bool
        Whether to analyze actuals
        If True, analyze actuals
        If False, ignore actuals
    blanking : bool
        Whether to blank repeated labels in the output for readability
        If True, repeated values in row columns are replaced with empty strings
        If False, all values are preserved as-is
    """

    parameters = {
        "Query" : label,
        "Directory" : path,
        "Flavor" : {
            "Name" : flavor,
            "Phase" : phase_re,
            "Participant" : participant_re,
            "Target" : target,
            "Actual" : actual
        },
        "Blanking" : blanking
    }

    # Run GUI
    result = visualize_query(parameters)

    return result

if __name__ == "__main__":
    # Debug values (remove '# [text]')
    label = "" # "Queries_Target_v2"
    path = "" # r"/home/fzvial/Documents/Work/CLD Lab/Phon Query Testing/Testing/full"
    flavor = "" # "TX"
    phase_re = "" # r"BL-\d{1,2}|Post-\dmo|Pre|Post|Mid|Tx-\d{1,2}"
    participant_re = "" # r"\w\d\d\d"
    target = False # True
    actual = False # True
    blanking = False # True

    # Execute function
    output = phon_query_to_csv(
        label = label,
        path = path,
        flavor = flavor,
        phase_re = phase_re,
        participant_re = participant_re,
        target = target,
        actual = actual,
        blanking = blanking
    )
