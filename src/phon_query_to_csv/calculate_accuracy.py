

import logging
import os
import pandas as pd
from phon_query_to_csv.logging_config import setup_logging
from phon_query_to_csv.calculate_accuracy_helper import get_accuracy

log = setup_logging(logging.INFO, __name__)

def _format_feature_map(feature_map):
    if not feature_map:
        return "{}"

    return ", ".join(f"{k}={v}" for k, v in feature_map.items())

# Step 3: Create accuracy columns in dataframe
def calculate_accuracy(filepath, nan_policy="max"):
    """
    Calculate accuracy metrics based on IPA Target and IPA Actual columns in a CSV file.

    Args:
        filepath (str): The path to the CSV file.
        nan_policy (str): Policy for handling unclassified articulations ('nan').
            Supported values: 'max', 'mid', 'zero'

    Returns:
        DataFrame: The updated DataFrame with accuracy metrics.
    """

    error_log_entries = ["Accuracy Error Log\n"]
    error_count = 0
    
    output_filename = "data_accuracy.csv"
    # Read the CSV file into a DataFrame
    df = pd.read_csv(filepath, encoding="utf-8")

    # Create mask to derive accurate and inaccurate phones
    accuracy_mask = df["IPA Target"] == df["IPA Actual"]

    # Initialize columns with default values
    df["Accuracy"] = float(0)

    print("Processing Accuracy...")

    # Assign values to columns based on masks
    df.loc[accuracy_mask, "Accuracy"] = float(1)

    acc_check = (idx for idx in df.index if not df.at[idx, "Accuracy"])

    for idx in acc_check :
        print(idx, "/", len(df.index))
        accuracy, msg, debug_info = get_accuracy(
            df.at[idx, "Alignment"],
            df.at[idx, "Analysis"],
            nan_policy=nan_policy,
            return_debug=True
        )
        df.at[idx, "Accuracy"] = accuracy
        nan_events = debug_info["nan_events"]
        fallback_events = debug_info["fallback_events"]

        if nan_events:
            error_log_entries.append(f"\nNAN feature mapping at entry {idx}\n")
            error_log_entries.append(
                f"\tTarget-Actual: {df.at[idx, 'IPA Target']} ↔ {df.at[idx, 'IPA Actual']}\n"
            )
            error_log_entries.append(
                f"\tAlignment: {df.at[idx, 'Alignment']}\n"
            )
            error_log_entries.append(
                f"\tAnalysis: {df.at[idx, 'Analysis']} | Accuracy: {accuracy}\n"
            )

            for event in nan_events:
                error_log_entries.append(
                    "\tNAN parameter: {parameter} | Pair: {target_phone} ↔ {actual_phone} | "
                    "Mapped: {target_articulation} ↔ {actual_articulation} | "
                    "Penalty: {penalty} | Policy: {nan_policy}\n".format(**event)
                )
                error_log_entries.append(
                    f"\t\tTarget features: {_format_feature_map(event['target_features'])}\n"
                )
                error_log_entries.append(
                    f"\t\tActual features: {_format_feature_map(event['actual_features'])}\n"
                )

        if fallback_events:
            error_log_entries.append(f"\nFallback category mapping at entry {idx}\n")
            error_log_entries.append(
                f"\tTarget-Actual: {df.at[idx, 'IPA Target']} ↔ {df.at[idx, 'IPA Actual']}\n"
            )
            error_log_entries.append(
                f"\tAlignment: {df.at[idx, 'Alignment']}\n"
            )
            error_log_entries.append(
                f"\tAnalysis: {df.at[idx, 'Analysis']} | Accuracy: {accuracy}\n"
            )

            for event in fallback_events:
                if event["event_type"] == "fallback_used":
                    error_log_entries.append(
                        "\tFallback {parameter} ({role} {phone}) -> {selected_label} | "
                        "mismatches={mismatches}/{compared} | compared={compared_features} | "
                        "rule={rule}\n".format(**event)
                    )
                    error_log_entries.append(
                        f"\t\tFeatures: {_format_feature_map(event['features'])}\n"
                    )
                elif event["event_type"] == "manual_override":
                    error_log_entries.append(
                        "\tManual override {parameter} ({role} {phone}) -> {selected_label} | "
                        "reason={reason}\n".format(**event)
                    )
                    error_log_entries.append(
                        f"\t\tFeatures: {_format_feature_map(event['features'])}\n"
                    )
                else:
                    error_log_entries.append(
                        "\tFallback unresolved {parameter} ({role} {phone})\n".format(**event)
                    )
                    error_log_entries.append(
                        f"\t\tFeatures: {_format_feature_map(event['features'])}\n"
                    )

        if msg:
            error_log_entries.append("\nError at entry " + str(idx) + " : " + msg + "\n")
            error_log_entries.append("\tAlignment ~ " + str(df.at[idx, "Alignment"]) + "\n")

            error_count += 1

    error_log_entries.append(f"\nTotal Error Count - {error_count}\n")
    error_log_entries.append("\n\nSpecifications\n")

    # Save the updated DataFrame to a new CSV file
    print(f"Generating {output_filename}...")

    output_filepath = os.path.join(os.path.dirname(filepath), output_filename)
    df.to_csv(output_filepath, encoding="utf-8", index=False)

    print(f"Saved {output_filename}")

    errlog_filepath = "accuracy_error_log.log"

    with open(errlog_filepath, mode = 'w') as file:
        for error in error_log_entries:
            file.write(error)

    print(f"Saved {errlog_filepath}")

    return output_filepath
