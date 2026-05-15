# -*- coding: utf-8 -*-

"""
Algorithm for automating pivot table construction from completed Phon analysis

Generates:
- 'pivot_table_dataset.csv' : Slice of data from full_annotated_dataset.csv
  fitted to pivot table with specifications determined from user input

Created on Fri Jul 11 09:14:22 2025
@modified: 2026-05-15
@author: Francesco Vial
"""

import pandas as pd
import os

def create_pivot_table(
    directory,
    dataframe,
    specifications,
    blanking,
    output_filename = 'pivot_table_dataset.csv'
):
    """
    Create a pivot table from the full annotated dataset.
    
    Parameters:
    -----------
    directory : str
        Directory path containing the data files
    dataframe : DataFrame
        DataFrame of the final table before pivoting
    specifications : dict
        Dictionary holding values for index, values, and aggfunc for pivoting
    blanking : bool
        Whether to blank repeated labels in the output for readability
        If True, repeated values in row columns are replaced with empty strings
        If False, all values are preserved as-is
    output_filename : str, default 'pivot_table_dataset.csv'
        Name of the output CSV file
    """
    
    out_fp = os.path.join(directory, 'Compiled', 'merged_files', output_filename)

    rows = specifications["Index"]
    vals = specifications["Values"]
    func = specifications["Aggfunc"]

    # Create pivot table
    try:
        out_df = dataframe.pivot_table(index = rows.keys(), values = vals, aggfunc = func)
    except Exception as e:
        print(f"Error creating pivot table: {e}")
        return
    
    filters = {}

    for row in rows.keys():
        valid = []

        for filter in rows[row].keys():
            if rows[row].get(filter):
                valid.append(filter)

        filters[row] = valid

    # Apply subrow filters
    for row, valid in filters.items():
        out_df = out_df[out_df.index.get_level_values(row).isin(valid)]

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
    os.makedirs(os.path.dirname(out_fp), exist_ok = True)
    out_df.to_csv(out_fp, index = False)

    print("Generated", output_filename)

    return directory

# Example usage for testing
if __name__ == "__main__":
    directory = ''

    create_pivot_table(directory)
