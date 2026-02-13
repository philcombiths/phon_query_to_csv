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
import os

from phon_query_to_csv.logging_config import setup_logging
from phon_query_to_csv.gen_csv import gen_csv
from phon_query_to_csv.merge_csv import merge_csv
from phon_query_to_csv.calculate_accuracy import calculate_accuracy
from phon_query_to_csv.phone_data_expander import phone_data_expander
from phon_query_to_csv.create_pivot_table import create_pivot_table
# from phon_query_to_csv.column_match import column_match # Optional

log = setup_logging(logging.INFO, __name__)

def _compiled_merged_path(directory, filename):
    return os.path.join(directory, "Compiled", "merged_files", filename)

def _require_existing_file(path, step_name, guidance):
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Required input for step '{step_name}' not found: {path}. {guidance}"
        )

def phon_query_to_csv(
    directory,
    query,
    phase_re,
    participant_re,
    overwrite=False,
    target=True,
    actual=True,
    nan_policy="max",
    run_gen_csv=True,
    run_merge=True,
    run_accuracy=True,
    run_expand=True,
    run_pivot=True
):
    """
    Wrapper for sequence of functions.
    """
    run_directory = directory
    current_filepath = None
    result = None
    merged_data_path = None
    accuracy_data_path = None
    expanded_data_path = None

    if run_gen_csv:
        gen_csv_result = gen_csv(directory, query, phase_re, participant_re, overwrite=overwrite)
        run_directory = gen_csv_result[0]
    else:
        if not isinstance(run_directory, str):
            raise ValueError(
                "directory must be set when run_gen_csv=False, because existing Compiled outputs are reused."
            )
        compiled_dir = os.path.join(run_directory, "Compiled")
        if not os.path.isdir(compiled_dir):
            raise FileNotFoundError(
                f"'Compiled' directory not found: {compiled_dir}. "
                "Enable run_gen_csv or provide a directory with existing Compiled outputs."
            )

    merged_data_path = _compiled_merged_path(run_directory, "AllPart_AllLang_AllAnalyses_data.csv")
    accuracy_data_path = _compiled_merged_path(run_directory, "data_accuracy.csv")
    expanded_data_path = _compiled_merged_path(run_directory, "full_annotated_dataset.csv")

    if run_merge:
        current_filepath = merge_csv(run_directory)
    elif run_accuracy or run_expand:
        _require_existing_file(
            merged_data_path,
            "merge",
            "Enable run_merge=True to regenerate it."
        )
        current_filepath = merged_data_path

    if run_accuracy:
        if not target:
            log.info("Skipping accuracy step because target=False.")
        else:
            if current_filepath is None:
                _require_existing_file(
                    merged_data_path,
                    "accuracy",
                    "Enable run_merge=True or provide an existing merged dataset."
                )
                current_filepath = merged_data_path
            current_filepath = calculate_accuracy(current_filepath, nan_policy=nan_policy)

    if run_expand:
        if current_filepath is None:
            fallback_source = accuracy_data_path if (target and os.path.isfile(accuracy_data_path)) else merged_data_path
            _require_existing_file(
                fallback_source,
                "expand",
                "Enable run_merge/run_accuracy or provide existing compiled outputs."
            )
            current_filepath = fallback_source
        result = phone_data_expander(current_filepath, run_directory, target=target, actual=actual)
        print("***** full_annotated_dataset.csv generated successfully. *****\n")

    if run_pivot:
        if not run_expand:
            _require_existing_file(
                expanded_data_path,
                "pivot",
                "Enable run_expand=True or provide existing full_annotated_dataset.csv."
            )
        result = create_pivot_table(run_directory)
        print("***** pivot_table_dataset.csv generated successfully. *****\n")

    if result is not None:
        return result
    return current_filepath

# Interactive Module Execution
if __name__ == "__main__":
    # Default parameters
    directory = None
    query = None
    flavor = None
    overwrite = False
    target = True
    actual = True
    nan_policy = "max"
    run_gen_csv = True
    run_merge = True
    run_accuracy = True
    run_expand = True
    run_pivot = True

    # Set Parameters Here:
    directory = directory
    flavor = "tx"  # Specify flavor (see options below)
    overwrite = False
    run_accuracy = False

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
    print(
        f"directory: {directory}\nquery: {query}\nflavor: {flavor}\n"
        f"target: {target}\nactual: {actual}\nnan_policy: {nan_policy}\n"
        f"run_gen_csv: {run_gen_csv}\nrun_merge: {run_merge}\nrun_accuracy: {run_accuracy}\n"
        f"run_expand: {run_expand}\nrun_pivot: {run_pivot}\noverwrite:{overwrite}"
    )
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
        actual=actual,
        nan_policy=nan_policy,
        run_gen_csv=run_gen_csv,
        run_merge=run_merge,
        run_accuracy=run_accuracy,
        run_expand=run_expand,
        run_pivot=run_pivot
    )
