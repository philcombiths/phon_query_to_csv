# -*- coding: utf-8 -*-

"""
Algorithm for automating pivot table construction from completed Phon analysis

Generates:
- 'pivot_table_dataset.csv' : Slice of data from full_annotated_dataset.csv
  fitted to pivot table with specifications determined from user input

Created on Fri Jul 11 09:14:22 2025
@modified: 2025-07-25
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
  subrows = []
  vals = []

  # rows = ['Language', 'Analysis', 'IPA Target']
  # subrows = [[], ['Consonants', 'Onset Clusters'], []]
  # vals = ['Accuracy', 'mean']

  # Gather user input
  if rows == []:
    labels = ', '.join(in_df.columns)

    print('Possible Rows: ' + labels)
    res = input('\nWhich would you like to be your row(s)? Separate by comma: ')

    for row in res.split(', '):
      rows.append(row)

  if subrows == []:
    for row in range(len(rows)):
      to_add = []
      
      print('\nPossible Subrows: ' + ', '.join(in_df[rows[row]].unique()))
      res = input('\nProvide your subrow(s). Leave blank if none: ')

      for subrow in res.split(', '):
        to_add.append(subrow)

      subrows.append(to_add)

  if vals == []:
    labels = ', '.join([l for l in in_df.columns if l not in rows])

    print('\nPossible Values: ' + labels)
    res = input('\nWhich would you like to be your values? Only one label: ')

    vals.append(res)

    res = input('\nWhat aggfunc would you like to apply? Leave blank if none: ')

    vals.append(res)

  # Create preliminary pivot table
  out_df = in_df.pivot_table(index = rows, values = vals[0], aggfunc = vals[1])
  out_df = out_df[out_df.index.get_level_values(rows[1]).isin(subrows[1])]

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
