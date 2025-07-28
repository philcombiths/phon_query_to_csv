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

def create_pivot_table(directory):
  in_fp = os.path.join(
    directory, 'Compiled', 'merged_files', 'full_annotated_dataset.csv'
  )
  out_fp = os.path.join(
    directory, 'Compiled', 'merged_files', 'pivot_table_dataset.csv'
  )

  # Initialization of values
  in_df = pd.read_csv(in_fp, encoding = 'utf-8')

  rows = []
  subrow_filters = {}
  vals = []
  
  # DEBUG: Uncomment the following lines to set default values for rows, subrows, and vals
  # rows = ['Language', 'Analysis', 'IPA Target']
  # subrows = [[], ['Consonants', 'Onset Clusters'], []]
  # vals = ['Accuracy', 'mean']

  # Gather user input
  if rows == []:
    labels = ', '.join(in_df.columns)

    print('Possible Variables: ' + labels)
    res = input('\nWhich variables do you want to group by? (If multiple, will be embedded in order given.) \nSeparate by comma: ')

    for row in res.split(', '):
      rows.append(row)  

  for row in rows:
      unique_vals = [str(v) for v in sorted(in_df[row].dropna().unique())]
      print(f"\nPossible values for {row}: {', '.join(unique_vals)}")
      res = input(f"Which value(s) do you want to filter {row} by? Leave blank for no filtering: ").strip()

      if res:
          selected = [v.strip() for v in res.split(',')]
          valid_selected = [v for v in selected if v in unique_vals]
          
          if not valid_selected:
              print(f"⚠️ Warning: No valid values entered for {row}. Skipping filtering for this column.")
          else:
              subrow_filters[row] = valid_selected


  if vals == []:
    labels = ', '.join([l for l in in_df.columns if l not in rows])

    print('\nPossible Values: ' + labels)
    res = input('\nWhich would you like to be your values? Only one label: ')

    vals.append(res)

    # Ask for aggregation function
    valid_aggfuncs = ['mean', 'sum', 'count', 'min', 'max', 'median', 'std']
    print("\nAvailable aggregation functions: " + ', '.join(valid_aggfuncs))
    res = input("Which aggregation function would you like to apply? Default is 'mean': ").strip().lower()

    if res not in valid_aggfuncs:
        if res != "":
            print(f"⚠️ '{res}' is not a recognized aggregation function. Defaulting to 'mean'.")
        res = 'mean'

    vals.append(res)

  # Create preliminary pivot table
  out_df = in_df.pivot_table(index = rows, values = vals[0], aggfunc = vals[1])
  

  # Apply subrow filters
  for row, allowed_vals in subrow_filters.items():
      out_df = out_df[out_df.index.get_level_values(row).isin(allowed_vals)]

  out_df = out_df.round(2)

  out_df.to_csv(out_fp, index = True)

  # Clean up table presentation
  out_df = pd.read_csv(out_fp)

  for c in out_df.columns[:-1]:
    last = None

    for i in range(len(out_df)):
      curr = out_df.at[i, c]
      
      if curr == last:
        out_df.at[i, c] = ''
      else:
        last = curr

  out_df.to_csv(out_fp, index = False)

  # Summary output for user
  print("\nPivot Table Created")
  print(f"Output file: {out_fp}")
  print(f"Rows used: {', '.join(rows)}")

  if subrow_filters:
      print("Subrow filters applied:")
      for key, vals in subrow_filters.items():
          print(f"  - {key}: {', '.join(vals)}")
  else:
      print("No subrow filters applied.")

  print(f"Value column: {vals[0]}")
  print(f"Aggregation function: {vals[1]}")
  print("Values rounded to 2 decimal places.")
  print("Repeated row labels are blanked in the final CSV for readability.\n")


# This code is for testing purposes
if __name__ == "__main__":
    # Default parameters
    directory = None

    # Set Parameters Here:
    directory = '/Users/pcombiths/Downloads/data/S405 Prelim/phone_listings'  # Change this to your directory path

    if directory is not None:
        create_pivot_table(directory)
    else:
        print("Please specify a valid directory.")
