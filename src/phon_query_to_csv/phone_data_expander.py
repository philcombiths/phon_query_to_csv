"""
This module contains functions for expanding phone feature data in a DataFrame. 
Required:
- numpy
- pandas
- ipa_map from ipa_features
"""

# TODO: Draw on other required tables, including baseline phones to create additional cols

import logging
import os
from collections import OrderedDict

import numpy as np
import pandas as pd
from ipa_features import ipa_map
# from tqdm import tqdm # For progress bar

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
    
    # Use ipa_map from ipa_features to get segments with components and features
    def get_cols_each_segment(cell_string):
        """
        Wrapper function to generate columns for each segment of an IPA string.
        
        This helper function takes an IPA string and returns a list of column names to be
        added to a DataFrame. The column names are generated outside the function for 
        each segment of the IPA string and values for IPA features aregenerated using the 
        ipa_map.segment_generator() function. The resulting values are concatenated into a 
        single list, which is returned by the function.
        
        Args:
            cell_string (str): IPA string for which to generate features for its components.
            
        Returns:
            List[str]: List of feature values each segment of the IPA string.
        """
        seg_gen = ipa_map.segment_generator(cell_string)
        seg_cols = []
        seg_counter = 0
        for key in feature_cols:
            try:
                seg = next(seg_gen)
                seg_counter += 1
                seg_cols.append(seg.string) # A/T_ column
                seg_cols.append(seg.get_base()) # A/T__Base column
                for seg_feature in feature_cols[key]: # A/T_ feature columns
                    feature = seg_feature.split('_')[1]
                    seg_cols.append(seg.get_feature(feature))
            except StopIteration:
                # If there are no more segments in the IPA string
                seg_cols += [""] * (len(seg_cols_list) - len(seg_cols) - 1)
        # Prepend number of segments in transcription
        seg_cols = [seg_counter] + seg_cols
        return seg_cols

    if actual is True:
        df["ID-Actual-Lang"] = df["Participant"].astype(str) + df["IPA Actual"] + df["Language"]
        actual_seg_cols = ["A1", "A2", "A3"]
        feature_cols = OrderedDict()
        for col in actual_seg_cols:
            feature_cols.update({col: [f"{col}_{prop}" for prop in properties_seg]})
        
        # TODO: Handle vowel and diacritic features

        seg_cols_list = []
        seg_cols_list.append("Actual Num Segs")
        for key in feature_cols:
            seg_cols_list.append(key)
            seg_cols_list.append(f"{key}_Base")
            seg_cols_list.extend(feature_cols[key])
        
        try:
            df[seg_cols_list] = df['IPA Actual'].apply(get_cols_each_segment).apply(pd.Series)
        except IndexError as exc:
            raise ValueError("Processing 'IPA Actual' features columns error.") from exc
        df[seg_cols_list] = df[seg_cols_list].fillna("")


    if target is True:   
        df["ID-Target-Lang"] = df["Participant"] + df["IPA Target"] + df["Language"]
        target_seg_cols = ["T1", "T2", "T3"]
        feature_cols = OrderedDict()
        for col in target_seg_cols:
            feature_cols.update({col: [f"{col}_{prop}" for prop in properties_seg]})
            
        df["Target Type"] = np.where(
            df["IPA Target"].str.len() == 1,
            "C",
            np.where(df["IPA Target"].str.len() == 2, "CC", "CCC"),
        )
        
        seg_cols_list = []
        seg_cols_list.append("Target Num Segs")
        for key in feature_cols:
            seg_cols_list.append(key)
            seg_cols_list.append(f"{key}_Base")
            seg_cols_list.extend(feature_cols[key])
        
        try:
            df[seg_cols_list] = df['IPA Target'].apply(get_cols_each_segment).apply(pd.Series)
        except IndexError as exc:
            raise ValueError("Processing 'IPA Target' features columns error.") from exc
        df[seg_cols_list] = df[seg_cols_list].fillna("")
        
        # TODO: Handle IPA Target with diacritics or more than 3 characters
        
    output_filepath = os.path.join(
        directory, "Compiled", "merged_files", "full_annotated_dataset.csv"
    )
    df.to_csv(
        output_filepath,
        encoding="utf-8",
        index=False,
    )

    return df
