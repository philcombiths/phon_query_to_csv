
import logging
import os
import numpy as np
import pandas as pd
from collections import OrderedDict
from ipa_features import ipa_map
from tqdm import tqdm
from phon_query_to_csv.logging_config import setup_logging

log = setup_logging(logging.INFO, __name__)

# phone_data_expander [in progress]
def phone_data_expander(file_location, directory, target=True, actual=True):
    output_filepath = os.path.join(
        directory, "Compiled", "merged_files", "full_annotated_dataset.csv"
    )

    if not isinstance(file_location, pd.DataFrame):
        # If not, assume it's a file location and load the data
        df = pd.read_csv(file_location)
    else:
        df = file_location
    
    properties_seg = ["voice", "place", "manner", "sonority", "EML"]
    if target is True:   
        df["ID-Target-Lang"] = df["Participant"] + df["IPA Target"] + df["Language"]
        target_seg_cols = ["T1", "T2", "T3"]
        target_feature_cols = []
        df["Target Type"] = np.where(
            df["IPA Target"].str.len() == 1,
            "C",
            np.where(df["IPA Target"].str.len() == 2, "CC", "CCC"),
        )

        try:
            df['T1'] = df['IPA Target'].str[0]  # Get C1
            df['T2'] = df['IPA Target'].str[1]  # Get C2
            df['T3'] = df['IPA Target'].str[2]  # Get C3
        except IndexError as exc:
            raise ValueError("IPA Target must have <= 3 characters.") from exc
        # TODO: Handle IPA Target with diacritics or more than 3 characters
        
    if actual is True:
        df["ID-Actual-Lang"] = df["Participant"].astype(str) + df["IPA Actual"] + df["Language"]
        actual_seg_cols = ["A1", "A2", "A3"]
        actual_feature_cols = OrderedDict()
        for col in actual_seg_cols:
            actual_feature_cols.update({col: [f"{col}_{prop}" for prop in properties_seg]})
        
        # Use ipa_map from ipa_features to get segments with components and features
        def get_cols_each_segment(cell_string):
            """
            Wrapper function to generate columns for each segment of an IPA string.
            
            Returns: List of strings for new columns
            """
            seg_gen = ipa_map.segment_generator(cell_string)
            seg_cols = []
            
            for key in actual_feature_cols:
                try:
                    seg = next(seg_gen)
                    seg_cols.append(seg.base[0].string)
                    # seg_cols.append(seg.string) # A_ column
                    for seg_feature in actual_feature_cols[key]: # A_ feature columns
                        feature = seg_feature.split('_')[1]
                        seg_cols.append(seg.get_feature(feature))
                except StopIteration:
                    seg_cols.append("")
                    # seg_cols.append(np.nan)
            return seg_cols
        
        # TODO: Handle vowel and diacritic features
        
        actual_seg_cols_list = []
        for key in actual_feature_cols:
            actual_seg_cols_list.append(key)
            actual_seg_cols_list.extend(actual_feature_cols[key])
        
        # for col in tqdm(actual_seg_cols, desc="Processing by-segment feature columns"):
            # for prop in properties_seg:
        try:
            df[actual_seg_cols_list] = df['IPA Actual'].apply(get_cols_each_segment).apply(pd.Series)
        except IndexError as exc:
            raise ValueError(f"({col}, {prop} had issue.") from exc

        #df[['A1', 'A2', 'A3']] = df['IPA Actual'].apply(get_cols_each_segment).apply(pd.Series)
        
        # def get_each_base(cell_string):
        #     """Wrapper function to get each segment of an IPA string."""
        #     try:
        #         return ipa_map.get_bases(cell_string)
        #     except IndexError: # Handles 
        #         return np.nan

    df[actual_seg_cols_list] = df[actual_seg_cols_list].fillna("")

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
