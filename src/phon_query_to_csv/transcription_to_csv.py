# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 15:59:21 2020
@author: Philip Combiths

Converts transcription text to a csv for Phon import.

Example use case:
    
    trans_source = r"G:\My Drive\Instruction\SLHS 607\607 Fall 2020\Datasets\Joseph_Pre_Table.csv"
    trans_df, char_trans = convert_transcriptions(trans_source)
"""
from phon_ipa_parse import get_Phon_char_list
import pandas as pd

def convert_transcriptions(trans_source, transform=False, in_place=False):
    """
    Args:
        trans_source : str filepath of a csv with an 'IPA Actual', 'IPA Target'
            column or both.
        transform : bool to toggle transforming data into Phon-readable format
            (not yet implemented). Default=False
        in_place : bool to toggle replacing source file with revised file
            (not yet implemented). Default=False
        
    Generates revised csv with illegal chars replaced with alternatives.
    
    Returns tuple (DataFrame, list). DataFrame of revised table and list
        containing illegal character replacements.
        
    To Do: iterate through multiple files before asking for legal character
        alternatives. Currently must input for each iteraction of fx.
    
    """
    
    # Get Phon chars list
    xml_path=r"C:/Users/Philip/Documents/GitHub/phon/RESOURCES/parser/ipa.xml"
    char_group_dict = get_Phon_char_list(xml_path=xml_path)
    char_list = []   
    for group in char_group_dict:
        for char in char_group_dict[group]:
            char_list.append(char[0])
        
    # Import source transcriptions
    trans_df = pd.read_csv(trans_source, encoding='utf-8')

    # Compare source to list of legal chars to generate illegal_chars
    illegal_chars = []
    for col in trans_df.columns:
        if col == 'IPA Actual':
            for x in trans_df['IPA Actual'].to_string(index=False).split('\n'):
                for c in x.strip():
                    if c not in char_list:
                        illegal_chars.append(c) 
        if col == 'IPA Target':                        
            for x in trans_df['IPA Target'].to_string(index=False).split('\n'):
                for c in x:
                    if c not in char_list:
                        illegal_chars.append(c)
        else:
            continue
    
    illegal_chars = list(set(illegal_chars))    
    
    # Get user input for illegal character alternatives
    print('************************')
    print('Illegal characters located')
    for c in illegal_chars:
        print(f"\t{c}")
    char_trans = []
    for x in illegal_chars:
        print('Illegal character:')
        print(x)
        y = input('Enter legal character alternative: ')
        translate_pair = (x, y)        
        char_trans.append(translate_pair)      
    
    # Compile regex to identify illegal chars       
    pass     
    
    # Replace illegal chars in source transcription
    for col in trans_df.columns:
        if col == 'IPA Actual':
            for c in char_trans:
                trans_df['IPA Actual'] = trans_df['IPA Actual'].str.replace(c[0], c[1])
        if col == 'IPA Target':
            for c in char_trans:
                trans_df['IPA Target'] = trans_df['IPA Target'].str.replace(c[0], c[1])
    trans_df.to_csv('rev_csv', encoding='utf-8', index=False)
    print(f"{len(char_trans)} characters replaced")
    return trans_df, char_trans


            
    