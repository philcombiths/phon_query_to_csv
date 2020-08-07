# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 17:47:32 2020

@author: Philip
"""
import regex as re

def re_pattern(search_elements, split_on=None, prefix=None, suffix=None, groups=None):

    """
    Generates a regexPattern for searching for all elements of a str or 
        list input
       
    Args:
        search_elements : str or list of stings to find in search. If str, 
            specify str to split search elements in split_on
        prefix: str, default None. prefix to each entry
        suffix: str, default None. suffix to each entry
        groups: str, default None. 
            'capture' : creates capturing groups around each entry
            'noncapture' : creates noncapturing groups around each entry
    
    Requires regex as re.
    
    Returns compiled regex pattern and prints as string
    """
    if type(search_elements) == str:        
        warning = "If search_elements is a string, split_on str must be specified." 
        assert type(split_on) == str, warning
        search_elements = search_elements.split(split_on)    
    regexEntriesList = search_elements
    revRegexList = []
    for entry in regexEntriesList:
        if prefix != None:
            entry = prefix + entry
        if suffix != None:
            entry = entry + suffix
        if groups == 'capture':
            entry = '('+entry+')'
        if groups == 'noncapture':
            entry = '(?:'+entry+')'
        revRegexList.append(entry)
    pattern = re.compile(r'|'.join(revRegexList))
    print("*****************************************")
    print(r'|'.join(revRegexList))
    return pattern