# -*- coding: utf-8 -*-

"""
Algorithm for automating pivot table construction from completed Phon analysis

Generates:
- 'sorted_pt_dataset.csv' : Sorted pivot table from pivot_table_dataset.csv
  fitted to sorting specifications determined from user input

Created on Thu Aug 07 16:30:14 2025
@modified: 2025-08-15
@author: Francesco Vial
"""

import pandas as pd
import numpy as np
import os

def sort_pivot_table(
    directory,
    sort_type=None,
    idx_loc=0,
    val_loc=1,
    partition=0,
    part_loc=-3,
    subdiv=[],
    l_start=0,
    l_end=-2,
    output_filename='sorted_pt_dataset.csv',
    show_preview=True
):
    in_fp = os.path.join(directory, 'Compiled', 'merged_files', 'pivot_table_dataset.csv')
    out_fp = os.path.join(directory, 'Compiled', 'merged_files', output_filename)

    # Load dataset
    try:
        in_df = pd.read_csv(in_fp, encoding='utf-8')
    except FileNotFoundError:
        print(f"Error: File not found at {in_fp}")
        return

    # Prompt for sorting or skip
    if not sort_type:
        print('Possible Sorting Types: High-Low, Low-High')
        res = input('\nWhich sorting type do you want to use? (Enter one of the two types or press Enter to use not sort: ').strip()

        if res:
            sort_type = res

            if sort_type != "High-Low" and sort_type != "Low-High":
                print("No valid inputs provided. Opting not to sort.")
                return
        else:
            return

    # Create subdivisions of the dataframe
    for row in in_df.iterrows():
        if isinstance(row[val_loc].iloc[part_loc], str):
            if partition != row[idx_loc]:
                subdiv.append(in_df.iloc[partition:row[idx_loc]])

            partition = row[idx_loc]

    subdiv.append(in_df.iloc[partition:])

    # Sort each subdivision
    for s in range(len(subdiv)):
        labels = subdiv[s].iloc[l_start].tolist()[:l_end]

        for l in range(len(labels)):
            subdiv[s].iat[l_start, l] = np.nan

        if sort_type == 'High-Low':
            subdiv[s] = subdiv[s].sort_values(by='Accuracy', ascending=False)
        if sort_type == 'Low-High':
            subdiv[s] = subdiv[s].sort_values(by='Accuracy', ascending=True)

        for l in range(len(labels)):
            subdiv[s].iat[l_start, l] = labels[l]

    # Combine subdivisions and write DF to CSV
    out_df = pd.concat(subdiv)
    os.makedirs(os.path.dirname(out_fp), exist_ok=True)
    out_df.to_csv(out_fp, index=False)

    # Summary output
    print("\nPivot Table Sorted")
    print(f"Output file: {out_fp}")
    print(f"Sorting used: {sort_type}")

    if show_preview:
        print("\nPreview of pivot table:")
        print(out_df.head())

    return

# Example usage for testing
if __name__ == "__main__":
    directory = ''
    sort_pivot_table(directory)