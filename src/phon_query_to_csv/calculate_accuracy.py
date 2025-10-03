

import logging
import os
import pandas as pd
from phon_query_to_csv.logging_config import setup_logging
from phon_query_to_csv.calculate_accuracy_helper import get_score

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

    # Create mask to derive accurate and inaccurate phones
    accuracy_mask = df["IPA Target"] == df["IPA Actual"]

    # Initialize columns with default values
    df["Accuracy"] = 0

    print("Processing Accuracy...")

    # Assign values to columns based on masks
    df.loc[accuracy_mask, "Accuracy"] = 1

    acc_check = (idx for idx in df.index if df.at[idx, "Accuracy"])

    for idx in acc_check :
       df.at[idx, "Accuracy"] = get_score(df.at[idx, "IPA Target"], df.at[idx, "IPA Actual"])

    # Save the updated DataFrame to a new CSV file
    print(f"Generating {output_filename}...")

    output_filepath = os.path.join(os.path.dirname(filepath), output_filename)
    df.to_csv(output_filepath, encoding="utf-8", index=False)

    print(f"Saved {output_filename}")

    return output_filepath

