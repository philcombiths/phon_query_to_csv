
import io
import logging
import os
import re
import shutil
import sys
import pandas as pd
from phon_query_to_csv.logging_config import setup_logging
from phon_query_to_csv.context_manager import enter_dir, change_dir


log = setup_logging(logging.INFO, __name__)

# Step 1: Transforms to uniform structure csv files
def gen_csv(directory, query, phase_re, participant_re, overwrite=False):
    """
    Formats a directory or subdirectories containing csv Phon query output files
    with unified column structure for input into merge_csv to generate a single
    master data file.

    Args:
        directory : directory path for original Phon query output files
        query : string specifying Phon query name

    Note: participant, phase, language, analysis variables must be modified to
        specify or extract values from the current data structure. These values
        are usually extracted from the filename str or containing directory
        name str (see lines 143-167).

    Generates a new csv file in "Compiled/uniform_files" directory for each
        processed output file.

    Returns:
        tuple: (participant_list, phase_list, language_list, analysis_list, file_count)
    """

    participant_list = []
    phase_list = []
    language_list = []
    analysis_list = []
    probe_list = []
    probe_type_list = []
    file_count = 0
    
    # If directory is None, request input for directory path
    while directory is None or not os.path.isdir(directory):
        directory = input("Please enter a valid directory path: ")
    if not overwrite: 
        try:
            assert "Compiled" not in os.listdir(
                directory
            ), "Compiled directory already exists. Must be moved or remove before executing script."
        except AssertionError as e:
            print(e)
            response = input(
                "Do you want to delete the existing 'Compiled' directory? (y/n): "
            )
            if response.lower() == "y":
                shutil.rmtree(os.path.join(directory, "Compiled"))
                print("Existing 'Compiled' directory has been deleted.")
            else:
                sys.exit("Exiting script.")
    else:
        shutil.rmtree(os.path.join(directory, "Compiled"))
        print("Existing 'Compiled' directory has been deleted.")    
    with change_dir(os.path.normpath(directory)):
        for dirName, subdirList, fileList in os.walk(os.getcwd()):
            # Skip 'Compiled' or '.bak' directories if already present"
            if any(x in dirName for x in ["Compiled", ".bak"]):
                continue
            ## Check for Excel files in directory
            if any(fname.endswith(".xls") for fname in os.listdir(dirName)):
                log.warning("**Excel files located in this directory:")
                log.warning(dirName)
                log.critical(dirName)
            if any(fname.endswith(".xlsx") for fname in os.listdir(dirName)):
                log.warning("**Excel files located in this directory:")
                log.warning(dirName)
                log.critical(dirName)
            ## Check for CSV files in directory
            if not any(fname.endswith(".csv") for fname in os.listdir(dirName)):
                log.warning("**No .csv files located in this directory:")
                log.warning(dirName)
            log.info("extracting from %s" % dirName)
            try:
                os.makedirs(os.path.join(directory, "Compiled", "uniform_files"))
            except:  # Removed "WindowsError" for MacOS compatibility
                log.warning(sys.exc_info()[1])
                log.warning("Compiled Data directory already created.")
            for cur_csv in os.listdir(dirName):
                # Skip other files (listed below) if they occurr
                if cur_csv in ["full_annotated_dataset.csv", 
                               "data_accuracy.csv", 
                               "AllPart_AllLang_AllAnalyses_data.csv"]:
                    print(cur_csv, " skipped")
                    continue
                if "Summary" in cur_csv:
                    print(cur_csv, " skipped")
                    continue
                # Include only CSV files
                if cur_csv.endswith(".csv"):
                    file_count += 1
                    with io.open(
                        os.path.join(dirName, cur_csv), mode="r", encoding="utf-8"
                    ) as current_csv:
                        # create pandas DataFrame df from csv file
                        df = pd.read_csv(current_csv, encoding="utf-8")
                        ###################################################
                        #### Extract keyword and column values
                        df.rename(columns={"Record #": "Record"}, inplace=True)
                        df.rename(columns={"Group #": "Group"}, inplace=True)
                        df["filename"] = cur_csv
                        df["Query Source"] = query
                        analysis = re.findall(
                            r"Consonants|Onset Clusters|Coda Clusters|Final Singletons|Initial Singletons|Medial Singletons|Singletons|Vowels|Initial Clusters|Final Clusters|Onset and Adjunct|Nucleus|Coda and Appendix",
                            dirName,
                        )[0].replace(r"/", "")
                        analysis_list.append(analysis)
                        df["Analysis"] = analysis
                        phase = "unknown"  # Default if no phase identified
                        phase = next(
                            (
                                match
                                for match in re.findall(
                                    phase_re,
                                    cur_csv,
                                )
                                if match
                            ),
                            "unknown",
                        )
                        phase_list.append(phase)
                        df["Phase"] = phase
                        # More complex language identification based on dictionary
                        lang_dict = {
                            "PEEP": "English",
                            "Peep": "English",
                            "peep": "English",
                            "En": "English",
                            "eng": "English",
                            "EFE": "Spanish",
                            "Efe": "Spanish",
                            "efe": "Spanish",
                            "Sp": "Spanish",
                            "spa": "Spanish",
                            "else": "Unspecified",  # When Tx is in Spanish, otherwise set to Tx language
                        }
                        language = "Unspecified"  # Default language
                        for key, value in lang_dict.items():
                            if key in cur_csv:
                                language = value
                                break
                        # language = cur_csv.split(".")[0] # Look in filename for language
                        language_list.append(language)
                        df["Language"] = language
                        try:
                            participant = re.findall(
                                participant_re,
                                cur_csv,
                            )[0]
                        except IndexError as exc:
                            raise IndexError(
                                "No participant found in filename. Is flavor set correctly?"
                            ) from exc

                        participant_list.append(participant)
                        df["Participant"] = participant
                        # Add column of Speaker ID extracted from filename
                        df["Speaker"] = participant
                        ###################################################
                        print(
                            "***********************************************\n",
                            list(df),
                        )
                        probe = cur_csv.split("_")[1]
                        probe_list.append(probe)
                        df["Probe"] = probe
                        probe_type = phase
                        probe_type_list.append(probe_type)
                        df["Probe Type"] = probe_type

                        # Apply transformation to 'Result' series to generate new columns
                        derive_dict = {
                            "IPA Alignment": lambda x: x.split(";", 1)[0].strip(),
                            # "IPA Target": lambda x: x.split(";", 1)[0] # Redundant with IPA Target column
                            # .strip()
                            # .split("↔")[0]
                            # .strip(),
                            # "IPA Actual": lambda x: x.split(";", 1)[0] # Redundant with IPA Actual column
                            # .strip()
                            # .split("↔")[1]
                            # .strip(),
                            "Tiers": lambda x: x.split(";", 1)[1].strip(),
                            "Notes": lambda x: x.split(";", 1)[1].split("↔")[-1][3:],
                            "Orthography": lambda x: x.split(";", 1)[1]
                            .split(",")[0]
                            .strip(),
                            "IPA Target Words": lambda x: x.split(";", 1)[1]
                            .split(",")[1]
                            .strip(),
                            "IPA Actual Words": lambda x: x.split(";", 1)[1]
                            .split(",")[2]
                            .strip(),
                            "IPA Alignment Words": lambda x: (
                                re.search(
                                    r" (\S+↔\S+,)+", x
                                )  # updated to allow for no data (when transcription empty)
                                .group(0)
                                .strip()[:-1]
                                if re.search(r" (\S+↔\S+,)+", x) is not None
                                else ""
                            ),
                        }

                        for key in derive_dict.keys():
                            df[key] = df["Result"].apply(derive_dict[key])

                        df["IPA Target"] = df["IPA Target"].replace(
                            {"g": "ɡ"}, regex=True
                        )
                        df["IPA Actual"] = df["IPA Actual"].replace(
                            {"g": "ɡ"}, regex=True
                        )

                        # Save REV_csv, UTF-8
                        log.info("Current working directory" + os.getcwd())
                        try:
                            df.to_csv(
                                os.path.join(
                                    directory,
                                    "Compiled",
                                    "uniform_files",
                                    "%s_%s_%s_%s_%s_%s.csv"
                                    % (
                                        participant,
                                        language,
                                        phase,
                                        analysis,
                                        probe,
                                        probe_type,
                                    ),
                                ),
                                encoding="utf-8",
                                index=False,
                            )
                        except FileNotFoundError:
                            log.error(sys.exc_info()[1])
                            log.error("Compiled Data folder not yet created")
        return (
            directory,
            set(participant_list),
            set(phase_list),
            set(language_list),
            set(analysis_list),
            set(probe_list),
            set(probe_type),
            file_count,
        )
