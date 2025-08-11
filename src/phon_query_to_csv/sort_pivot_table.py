# -*- coding: utf-8 -*-

"""
Algorithm for automating pivot table construction from completed Phon analysis

Generates:
- 'pivot_table_dataset.csv' : Sorted pivot table from file of the same name
  fitted to sorting specifications determined from user input

Created on Thu Aug 07 16:30:14 2025
@modified: 2025-08-11
@author: Francesco Vial
"""

import pandas as pd
import os

def sort_pivot_table(
    directory,
    sort_type
):
    # Take in pivot_table_dataset.csv
    # Ask user if they would like it sorted
    # If no, terminate function
    # If yes, ask whether high-low or low-high sorting
    
    # Convert CSV file to DF

    # Iterate through to find groupings (look for partitions of secondary indices)
      # Mark a location as a grouping boundary based on the third to last column returning a value
      # Do not include the first row

    # Split DF into subsections according to gathered groupings (use loc())
    # sort_values() for each grouping
    # Stitch the subsections back together into a full DF

    # Convert DF to CSV file
    return

# Example usage for testing
if __name__ == "__main__":
    directory = '~/Documents/Work/CLD Lab/Phon Query Testing'
    sort_pivot_table(directory)