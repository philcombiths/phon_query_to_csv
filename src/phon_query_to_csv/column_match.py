
import csv
import logging
import os
import pandas as pd
from phon_query_to_csv.logging_config import setup_logging

log = setup_logging(logging.INFO, __name__)
# Step 3 (optional): Organizes and renames columns according to column_alignment.csv
def column_match(
    table_to_modify,
    column_key="column_alignment.csv",
    table_to_match=None,
    output_filename="compatible_data",
):
    """
    Rearranges and renames columns in a DataFrame or CSV table to fit column
    structure specified in a column_key.

    Args:
        table_to_modify : file path, buffer object, or DataFrame
        column_key : file path. Default = 'column_alignment.csv'
        table_to_match : file path (optional). Default = None.
        output_filename : str. Default = "compatible_data"

    Generates output_filename csv file

    Returns:
        tuple: (new_table, actual_cols_omitted_renamed, actual_cols_added)
    """

    # Import table_to_modify as DataFrame
    try:
        if os.path.isfile(table_to_modify):
            table_directory = os.path.dirname(table_to_modify)
            print("'table_to_modify' input is a filepath.")
            table_to_modify = pd.read_csv(table_to_modify, encoding="utf-8")
    except:
        pass
    else:
        table_directory = None
        if isinstance(table_to_modify, pd.DataFrame):
            print("'table_to_modify' input is a DataFrame already.")
            warning = (
                "table_to_modify must be valid file path, buffer object, or DataFrame"
            )
        assert type(table_to_modify) == pd.core.frame.DataFrame, warning
    new_table = table_to_modify
    # os.path.join(table_directory,
    with open(column_key, mode="r") as key_file:
        key_reader = csv.reader(key_file)
        # Extract column information
        for i, row in enumerate(key_reader):
            if i == 2:
                target_cols = row
            if i == 3:
                actual_cols = row

        # Check actual columns
        actual_cols_omitted_renamed = []
        actual_cols_added = []
        for col in list(table_to_modify.columns):
            if col not in actual_cols:
                actual_cols_omitted_renamed.append(col)
        for col in actual_cols:
            if col not in list(table_to_modify.columns):
                actual_cols_added.append(col)
        # Rename actual columns
        for col_name_pair in zip(target_cols, actual_cols):
            if col_name_pair[1] == "":
                continue
            elif col_name_pair[0] != col_name_pair[1]:
                new_table = new_table.rename(
                    columns={col_name_pair[1]: col_name_pair[0]}
                )
        new_table = new_table.reindex(columns=target_cols)

        # Potential enhancement: Use optional table_to_match to import XLSX and test for compatibility.

        # Check new table
        valid_transformation = True
        if list(new_table.columns) == target_cols:
            pass
        elif len(list(new_table.columns)) < target_cols:
            print("WARNING: Target column(s) unaccounted for")
            valid_transformation = False
        for i, col_name_pair in enumerate(zip(list(new_table.columns), target_cols)):
            if col_name_pair[0] != col_name_pair[1]:
                if i < len(target_cols):
                    print("WARNING: Column mismatch")
                    valid_transformation = False
                else:
                    print(f"Column {col_name_pair[1]} appended.")
        if valid_transformation == True:
            print("*****************************")
            print("Valid transformation achieved.")
        else:
            print("*****************************")
            print(
                "WARNING: Valid transformation NOT achieved. Check file when complete."
            )
        print("Creating file...")

        output_filepath = os.path.join(
            directory, "Compiled", "merged_files", f"{output_filename}.csv"
        )
        new_table.to_csv(
            output_filepath,
            encoding="utf-8",
            index=False,
        )
        print("CSV file Generated:", os.path.abspath(output_filepath))
        print("Process complete.")
        return (new_table, actual_cols_omitted_renamed, actual_cols_added)

