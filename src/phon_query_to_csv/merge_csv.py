
import csv
import glob
import io
import os
import shutil
import sys
import logging
from phon_query_to_csv.logging_config import setup_logging

log = setup_logging(logging.INFO, __name__)

# Step 2: Merges uniformly structured csv files
def merge_csv(
    directory,
    participant_list=["AllPart"],
    language_list=["AllLang"],
    analysis_list=["AllAnalyses"],
    separate_participants=False,
    separate_languages=False,
    separate_analyses=False,
):
    """
    From a directory of uniformly structured csv files, merge into a single
    file or several files, as defined by fx argumments.

    Args:
        participant_list : list of participants to include, requires
            separate_participants=True. Default includes all.
        language_list : list of languages to include, requires
            separate_languages=True. Default includes all.
        analysis_list : list of analyses to include, requires
            separate_analyses=True. Default includes all.
        separate_participants : bool. Default=False
        separate_languages : bool. Default=False
        separate_analyses : bool. Default=False

    Returns str save_path

    Note: If a custom list is passed, corresponding "separate" variable must
        be set to True.
    """
    # Check for correct arguments
    if participant_list != ["AllPart"]:
        warning = (
            "If a custom participant_list is passed, separate_participants must = True"
        )
        assert separate_participants == True, warning
    if language_list != ["AllLang"]:
        warning = "If a custom language_list is passed, separate_languages must = True"
        assert separate_languages == True, warning
    if analysis_list != ["AllAnalyses"]:
        warning = "If a custom analysis_list is passed, separate_analyses must = True"
        assert separate_analyses == True, warning
    try:
        os.makedirs(os.path.join(directory, "Compiled", "merged_files"))
    # Was WindowsError for Windows operating system.
    except FileExistsError as e:
        log.warning(str(e))
        log.warning(sys.exc_info()[1])
        log.warning("Compiled Data directory already created.")
    for participant in participant_list:
        for language in language_list:
            for analysis in analysis_list:
                save_path = os.path.join(
                    directory,
                    "Compiled",
                    "merged_files",
                    f"{participant}_{language}_{analysis}_data.csv",
                )
                with io.open(save_path, "wb") as outfile:
                    log.info(outfile)
                    # participantdata = os.path.join(directory, 'Compiled Data', '%s*.csv' (participant))
                    if separate_participants:
                        if separate_languages:
                            if separate_analyses:
                                file_search_term = os.path.join(
                                    directory,
                                    "Compiled",
                                    "uniform_files",
                                    f"*{participant}*{language}*{analysis}*.csv",
                                )
                                # file_search_term = f"{directory}\\Compiled\\uniform_files\\*{participant}*{language}*{analysis}*.csv"
                            else:
                                file_search_term = os.path.join(
                                    directory,
                                    "Compiled",
                                    "uniform_files",
                                    f"*{participant}*{language}*.csv",
                                )
                        else:
                            if separate_analyses:
                                file_search_term = os.path.join(
                                    directory,
                                    "Compiled",
                                    "uniform_files",
                                    f"*{participant}*{analysis}*.csv",
                                )
                            else:
                                file_search_term = os.path.join(
                                    directory,
                                    "Compiled",
                                    "uniform_files",
                                    f"*{participant}*.csv",
                                )
                    else:
                        if separate_languages:
                            if separate_analyses:
                                file_search_term = os.path.join(
                                    directory,
                                    "Compiled",
                                    "uniform_files",
                                    f"*{language}*{analysis}*.csv",
                                )
                            else:
                                file_search_term = os.path.join(
                                    directory,
                                    "Compiled",
                                    "uniform_files",
                                    f"*{language}*.csv",
                                )
                        else:
                            if separate_analyses:
                                file_search_term = os.path.join(
                                    directory,
                                    "Compiled",
                                    "uniform_files",
                                    f"*{analysis}*.csv",
                                )
                            else:
                                file_search_term = os.path.join(
                                    directory, "Compiled", "uniform_files", "*.csv"
                                )
                    for i, fname in enumerate(glob.glob(file_search_term)):
                        with io.open(fname, "rb") as infile:
                            if i != 0:
                                infile.readline()  # Throw away header on all but first file
                            # Block copy rest of file from input to output without parsing
                            shutil.copyfileobj(infile, outfile)
                            log.info(fname + " has been imported.")
                    csv.writer(outfile)
                    log.info("Saved", outfile)

    return save_path
