
import logging
import os
import numpy as np
import pandas as pd
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
    
    component_cols=[]
    if target is True:   

        df["ID-Target-Lang"] = df["Participant"] + df["IPA Target"] + df["Language"]
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
        
        component_cols += ["T1", "T2", "T3"]
        
    if actual is True:
        df["ID-Actual-Lang"] = df["Participant"].astype(str) + df["IPA Actual"] + df["Language"]
        
        # Multi-segment rows to be processed separtely from single-segment rows  
        # single_segment_analyses = ['Initial Singletons', 'Consonants', 'Final Singletons', 'Singletons', 'Vowels']
        # multi_seg_rows = ~df['Analysis'].isin(single_segment_analyses) # not in single-segment rows assumed multi-segment
        
        # Use ipa_map from ipa_features to get segments with components and features
        ## Single-segment extraction?
        
        #df.loc[multi_seg_rows, 'A1'] = df.loc[multi_seg_rows, 'IPA Actual'].apply(lambda x: ipa_map.get_bases(x)[0])
        
        ## Multi-segment extraction
        def get_each_segment_str(cell_string):
            """
            Wrapper function to get each segment of an IPA string.
            
            Returns: List of string for each segment or np.nan if no segment
            """
            seg_gen = ipa_map.segment_generator(cell_string)
            seg_cols = []
            for _ in range(3):                
                try:
                    seg_cols.append(next(seg_gen).string)
                except StopIteration:
                    seg_cols.append(np.nan)
            return seg_cols
        
# result = df.apply(get_each_segment_str, axis=1, result_type='expand')
# if len(result.columns) != len(['A1', 'A2', 'A3']):
#     raise ValueError("Columns must be same length as key")
# df[['A1', 'A2', 'A3']] = result
        df[['A1', 'A2', 'A3']] = df['IPA Actual'].apply(get_each_segment_str).apply(pd.Series)

        component_cols += ["A1", "A2", "A3"]
        # def get_each_base(cell_string):
        #     """Wrapper function to get each segment of an IPA string."""
        #     try:
        #         return ipa_map.get_bases(cell_string)
        #     except IndexError: # Handles 
        #         return np.nan
                

    
        # df['A1'] = df['IPA Actual'].apply(lambda x: get_each_base(x, 0))
        # df['A2'] = df['IPA Actual'].apply(lambda x: get_each_base(x, 1))
        # # For each row in df, if IPA Actual len is >1, fill 'A2' cell with get_bases( IPA Actual )[1] to the segment
        # df.loc[df['IPA Actual'].str.len() > 1, 'A2'] = df.loc[df['IPA Actual'].str.len() > 1, 'IPA Actual'].apply(lambda x: ipa_map.get_bases(x)[1])
        # df.loc[df['IPA Actual'].str.len() > 2, 'A3'] = df.loc[df['IPA Actual'].str.len() > 2, 'IPA Actual'].apply(lambda x: ipa_map.get_bases(x)[2])
        
    
        # Actual segments not accurate because diacritics are treated as segments.
        # df["A1"] = df["IPA Actual"].str[0]  # Get C1
        # df["A2"] = df["IPA Actual"].str[1]  # Get C2
        # df["A3"] = df["IPA Actual"].str[2]  # Get C3
        # df["A4"] = df["IPA Actual"].str[3]  # Get C4
        # df["A5"] = df["IPA Actual"].str[4]  # Get C5
    # Fill NaN with empty string ''
    # component_cols = ["T1", "T2", "T3", "A1", "A2", "A3"]
    df[component_cols] = df[component_cols].fillna("")

    properties = ["voice", "place", "manner", "sonority"]
    for col in tqdm(component_cols, desc="Processing by-segment feature columns"):
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
