
import logging
import os
import numpy as np
import pandas as pd
from ipa_features import ipa_map
from tqdm import tqdm
from phon_query_to_csv.logging_config import setup_logging

log = setup_logging(logging.INFO, __name__)

# phone_data_expander [in progress]
def phone_data_expander(file_location, directory):
    output_filepath = os.path.join(
        directory, "Compiled", "merged_files", "full_annotated_dataset.csv"
    )

    if not isinstance(file_location, pd.DataFrame):
        # If not, assume it's a file location and load the data
        df = pd.read_csv(file_location)
    else:
        df = file_location
    # Generate ['ID-Target-Lang'] column
    df["ID-Target-Lang"] = df["Participant"] + df["IPA Target"] + df["Language"]
    try:  # Don't generate from Target columns if queries don't have Targets
        # Generate ['Target Type'] column
        df["Target Type"] = np.where(
            df["IPA Target"].str.len() == 1,
            "C",
            np.where(df["IPA Target"].str.len() == 2, "CC", "CCC"),
        )
        # Generate Target and Actual columns for each consonant in clusters
        df["T1"] = df["IPA Target"].str[0]  # Get C1
        df["T2"] = df["IPA Target"].str[1]  # Get C2
        df["T3"] = df["IPA Target"].str[2]  # Get C3
    except AttributeError:
        df["Target Type"] = ""
        df["T1"] = ""  # Get C1
        df["T2"] = ""  # Get C2
        df["T3"] = ""  # Get C3
    # Actual segments not accurate because diacritics are treated as segments.
    df["A1"] = df["IPA Actual"].str[0]  # Get C1
    df["A2"] = df["IPA Actual"].str[1]  # Get C2
    df["A3"] = df["IPA Actual"].str[2]  # Get C3
    df["A4"] = df["IPA Actual"].str[3]  # Get C4
    df["A5"] = df["IPA Actual"].str[4]  # Get C5
    # Fill NaN with empty string ''
    columns = ["T1", "T2", "T3", "A1", "A2", "A3", "A4", "A5"]
    df[columns] = df[columns].fillna("")

    properties = ["voice", "place", "manner", "sonority"]
    for col in tqdm(columns, desc="Processing by-segment feature columns"):
        for prop in properties:
            df[f"{col}_{prop}"] = df[col].apply(
                lambda x: getattr(ipa_map.PhoElement(x), prop, "") if x else ""
            )

    columns_more = ["IPA Target", "IPA Actual"]
    properties_more = ["voice", "place", "manner", "sonority", "EML"]
    for col in tqdm(
        columns_more, desc="Processing features for IPA Target/Actualcolumns"
    ):
        for prop in properties_more:
            df[f"{col}_{prop}"] = df[col].apply(
                lambda x: getattr(ipa_map.PhoElement(x), prop, "") if x else ""
            )
            # TODO Make this work for the main segment regardless of diacritics.

    output_filepath = os.path.join(
        directory, "Compiled", "merged_files", "full_annotated_dataset.csv"
    )
    df.to_csv(
        output_filepath,
        encoding="utf-8",
        index=False,
    )

    return df

    # For all the 'T1', 'T2', 'T3','A1', 'A2', 'A3', 'A4', 'A5' columns that contain IPA:
    # extract sonority, manner, voice, place as new columns in the df using ipa_map.py
    # When Type== "CC"
    # Sonority distance
    # For each component,
    # For each component phoneme:
    #   Create df columns for each of the useful feature details:
    #   sonority, manner, voice, place, class
    #   Use the IPA table project already started
    # Draw on other required tables, including baseline phones to create additional cols
