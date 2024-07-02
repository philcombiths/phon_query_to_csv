

import logging
import os
import pandas as pd
from phon_query_to_csv.logging_config import setup_logging

log = setup_logging(logging.INFO, __name__)

# Step 3: Create accuracy columns in dataframe
def calculate_accuracy(filepath):
    """
    Calculate accuracy metrics based on IPA Target and IPA Actual columns in a CSV file.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        DataFrame: The updated DataFrame with accuracy metrics.
    """
    output_filename = "data_accuracy.csv"
    # Read the CSV file into a DataFrame
    df = pd.read_csv(filepath, encoding="utf-8")

    # Create masks to derive accurate, substituted, and deleted phones
    accurate_mask = df["IPA Target"] == df["IPA Actual"]
    inaccurate_mask = df["IPA Target"] != df["IPA Actual"]
    deletion_mask = (
        df["IPA Actual"].isin([pd.NaT, "", " ", "∅"]) | df["IPA Actual"].isnull()
    )
    substitution_mask = (df["IPA Target"] != df["IPA Actual"]) & (~deletion_mask)

    # Initialize columns with default values
    df["Accuracy"] = 0
    df["Deletion"] = 0
    df["Substitution"] = 0

    print("Processing Accuracy, Deletion, Substitution...")

    # Assign values to columns based on masks
    df.loc[accurate_mask, "Accuracy"] = 1
    df.loc[deletion_mask, "Deletion"] = 1
    df.loc[substitution_mask, "Substitution"] = 1

    # Save the updated DataFrame to a new CSV file
    print(f"Generating {output_filename}...")

    output_filepath = os.path.join(os.path.dirname(filepath), output_filename)
    df.to_csv(output_filepath, encoding="utf-8", index=False)

    print(f"Saved {output_filename}")

    return output_filepath

