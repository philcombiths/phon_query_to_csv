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
    rows=None,
    value_column=None,
    aggfunc=None,
    subrow_filters=None,
    output_filename='pivot_table_dataset.csv',
    show_preview=True,
    blank_repeated_labels=True
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
    in_fp = os.path.join(directory, 'Compiled', 'merged_files', 'full_annotated_dataset.csv')
    out_fp = os.path.join(directory, 'Compiled', 'merged_files', output_filename)

    # Load dataset
    try:
        in_df = pd.read_csv(in_fp, encoding='utf-8')
    except FileNotFoundError:
        print(f"Error: File not found at {in_fp}")
        return

    # Prompt for rows or set default
    if not rows:
        default_rows = ['Participant', 'Phase', 'Language', 'Analysis', 'IPA Target']
        print('Possible Variables:', ', '.join(in_df.columns))
        res = input('\nWhich variables do you want to group by? (If multiple, will be embedded in order given.)\nSeparate by comma, or press Enter to use default: ').strip()

        if res:
            rows = [x.strip() for x in res.split(',') if x.strip() in in_df.columns]
            if not rows:
                print("No valid inputs provided. Using default grouping:")
                rows = [r for r in default_rows if r in in_df.columns]
                print(f"Default rows: {', '.join(rows)}")
        else:
            rows = [r for r in default_rows if r in in_df.columns]
            print(f"\nNo input provided. Using default grouping:")
            print(f"Default rows: {', '.join(rows)}")

    # Validate row selection
    for r in rows:
        if r not in in_df.columns:
            print(f"Error: '{r}' not found in dataset columns.")
            return

    # Initialize subrow filters
    if subrow_filters is None:
        subrow_filters = {}
        for row in rows:
            unique_vals = [str(v) for v in sorted(in_df[row].dropna().unique())]
            print(f"\nPossible values for {row}: {', '.join(unique_vals)}")
            res = input(f"Which value(s) do you want to filter {row} by? Leave blank for no filtering: ").strip()
            if res:
                selected = [v.strip() for v in res.split(',')]
                valid_selected = [v for v in selected if v in unique_vals]
                if valid_selected:
                    subrow_filters[row] = valid_selected
                else:
                    print(f"Warning: No valid values entered for {row}. Skipping filter.")

    # Select value column
    if not value_column:
        labels = ', '.join([l for l in in_df.columns if l not in rows])
        print('\nPossible Values:', labels)
        res = input('Which would you like to be your values? Only one label: ').strip()
        if res not in in_df.columns:
            print(f"Error: Value column '{res}' not found in dataset.")
            return
        value_column = res
    
    # Check if value column is numeric
    if not pd.api.types.is_numeric_dtype(in_df[value_column]):
        print(f"Error: Column '{value_column}' is not numeric and cannot be aggregated.")
        return

    # Select aggregation function
    valid_aggfuncs = ['mean', 'sum', 'count', 'min', 'max', 'median', 'std']
    if not aggfunc:
        print("\nAvailable aggregation functions: " + ', '.join(valid_aggfuncs))
        res = input("Which aggregation function would you like to apply? Default is 'mean': ").strip().lower()
        if res not in valid_aggfuncs:
            if res:
                print(f"Warning: '{res}' is not a recognized aggregation function. Defaulting to 'mean'.")
            aggfunc = 'mean'
        else:
            aggfunc = res
    elif aggfunc not in valid_aggfuncs:
        print(f"Warning: '{aggfunc}' is not a recognized aggregation function. Defaulting to 'mean'.")
        aggfunc = 'mean'


    # Create pivot table
    try:
        out_df = in_df.pivot_table(index=rows, values=value_column, aggfunc=aggfunc)
    except Exception as e:
        print(f"Error creating pivot table: {e}")
        return

    # Apply subrow filters
    for row, allowed_vals in subrow_filters.items():
        out_df = out_df[out_df.index.get_level_values(row).isin(allowed_vals)]

    # Prepare for output
    out_df = out_df.round(2).reset_index()

    # Blank repeated labels (optional)
    if blank_repeated_labels:
        for col in rows:
            last = None
            for i in range(len(out_df)):
                curr = out_df.at[i, col]
                if curr == last:
                    out_df.at[i, col] = ''
                else:
                    last = curr

    # Save to CSV
    os.makedirs(os.path.dirname(out_fp), exist_ok=True)
    out_df.to_csv(out_fp, index=False)

    # Summary output
    print("\nPivot Table Created")
    print(f"Output file: {out_fp}")
    print(f"Rows used: {', '.join(rows)}")
    if subrow_filters:
        print("Subrow filters applied:")
        for key, vals in subrow_filters.items():
            print(f"  - {key}: {', '.join(vals)}")
    else:
        print("No subrow filters applied.")
    print(f"Value column: {value_column}")
    print(f"Aggregation function: {aggfunc}")
    print("Values rounded to 2 decimal places.")
    if blank_repeated_labels:
        print("Repeated row labels are blanked in the final CSV for readability.")
    else:
        print("Repeated row labels are preserved in the final CSV.")

    if show_preview:
        print("\nPreview of pivot table:")
        print(out_df.head())

# Example usage for testing
if __name__ == "__main__":
    directory = ''
    # Default behavior (blanks repeated labels)
    create_pivot_table(directory)
    
    # To preserve repeated labels, set blank_repeated_labels=False
    # create_pivot_table(directory, blank_repeated_labels=False)
