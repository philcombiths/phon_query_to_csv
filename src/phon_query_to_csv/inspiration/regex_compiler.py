# -*- coding: utf-8 -*-
"""
Created on Thu Aug 6 2020
Updated on Wed Jul 2 2024

@author: Philip Combiths

NOTE: See also regex_find_generator from file_ops module for 
      a related function pulling from clipboard or csv column.
"""
import re


def re_pattern(search_elements, split_on=None, prefix=None, suffix=None, groups=None):
    """
    Generates a regexPattern for searching for each of the elements of a str or
        list input, separated by "or".

    Args:
        search_elements : str or list of stings to find in search. If str,
            specify str to split search elements in split_on
        prefix: str, default None. prefix to each entry
        suffix: str, default None. suffix to each entry
        groups: str, default None.
            'capture' : creates capturing groups around each entry
            'noncapture' : creates noncapturing groups around each entry

    Requires re module

    Returns compiled regex pattern and prints as string
    """
    if isinstance(search_elements, str):
        if split_on is None:
            raise ValueError(
                "If search_elements is a string, split_on must be specified."
            )
        search_elements = search_elements.split(split_on)
    regex_entries_list = search_elements
    rev_regex_list = []
    for entry in regex_entries_list:
        if prefix is not None:
            entry = prefix + entry
        if suffix is not None:
            entry = entry + suffix
        if groups == "capture":
            entry = "(" + entry + ")"
        if groups == "noncapture" or groups == "non-capture":
            entry = "(?:" + entry + ")"
        rev_regex_list.append(entry)
    pattern = re.compile(r"|".join(rev_regex_list))
    print("*****************************************")
    print(r"|".join(rev_regex_list))
    return pattern

if __name__ == "__main__":
    result = re_pattern('a b c d e f g h', split_on=' ', groups='noncapture')
