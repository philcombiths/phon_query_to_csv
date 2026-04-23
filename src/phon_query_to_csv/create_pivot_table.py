# -*- coding: utf-8 -*-

"""
Algorithm for automating pivot table construction from completed Phon analysis

Generates:
- 'pivot_table_dataset.csv' : Slice of data from full_annotated_dataset.csv
  fitted to pivot table with specifications determined from user input

Created on Fri Jul 11 09:14:22 2025
@modified: 2025-07-28
@author: Francesco Vial
"""

import pandas as pd
import os

def create_pivot_table(
    directory,
    dataframe,
    specifications,
    blanking = False,
    output_filename = 'pivot_table_dataset.csv'
):
    """
    Create a pivot table from the full annotated dataset.
    
    Parameters:
    -----------
    directory : str
        Directory path containing the data files
    rows : list, optional
        List of column names to use as rows in the pivot table
    value_column : str, optional
        Column name to use for values in the pivot table
    aggfunc : str, optional
        Aggregation function to apply ('mean', 'sum', 'count', etc.)
    subrow_filters : dict, optional
        Dictionary of filters to apply to specific row columns
    output_filename : str, default 'pivot_table_dataset.csv'
        Name of the output CSV file
    show_preview : bool, default True
        Whether to display a preview of the pivot table
    blank_repeated_labels : bool, default True
        Whether to blank repeated labels in the output for readability.
        If True, repeated values in row columns are replaced with empty strings.
        If False, all values are preserved as-is.
    """
    
    out_fp = os.path.join(directory, 'Compiled', 'merged_files', output_filename)

    # Create pivot table
    try:
        out_df = dataframe.pivot_table(index = specifications["Index"].keys(), values = specifications["Values"], aggfunc = specifications["Aggfunc"])
    except Exception as e:
        print(f"Error creating pivot table: {e}")
        return

    # Apply subrow filters
    for row in specifications["Index"].keys():
        out_df = out_df[out_df.index.get_level_values(row).isin(specifications["Index"][row].keys())]

    # Prepare for output
    out_df = out_df.round(2).reset_index()

    # Blank repeated labels (optional)
    if blanking:
        for var in specifications["Index"].keys():
            last = None

            for i in range(len(out_df)):
                curr = out_df.at[i, var]
                
                if curr == last:
                    out_df.at[i, var] = ''
                else:
                    last = curr

    # Save to CSV
    os.makedirs(os.path.dirname(out_fp), exist_ok=True)
    out_df.to_csv(out_fp, index=False)

    print("Generated", output_filename)

    return directory

# Example usage for testing
if __name__ == "__main__":
    directory = ''
    # Default behavior (blanks repeated labels)
    create_pivot_table(directory)
    
    # To preserve repeated labels, set blank_repeated_labels=False
    # create_pivot_table(directory, blank_repeated_labels=False)
