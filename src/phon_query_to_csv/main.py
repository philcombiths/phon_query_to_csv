import logging

from phon_query_to_csv.logging_config import setup_logging
from phon_query_to_csv.visualize_query import visualize_query

log = setup_logging(logging.INFO, __name__)

def phon_query_to_csv(label, path, flavor, phase_re, participant_re, target, actual, blanking):
    parameters = {
        "Query" : label,
        "Directory" : path,
        "Flavor" : {
            "Name" : flavor,
            "Phase" : phase_re,
            "Participant" : participant_re,
            "Target" : target,
            "Actual" : actual
        },
        "Blanking" : blanking
    }

    result = visualize_query(parameters)

    return result

if __name__ == "__main__":
    # Set defaults (for debugging)
    label = "Queries_Target_v2"
    path = r"/home/fzvial/Documents/Work/CLD Lab/Phon Query Testing/Testing/full"
    flavor = "TX"
    phase_re = r"BL-\d{1,2}|Post-\dmo|Pre|Post|Mid|Tx-\d{1,2}"
    participant_re = r"\w\d\d\d"
    target = True
    actual = True
    blanking = True

    # Execute function
    output = phon_query_to_csv(
        label = label,
        path = path,
        flavor = flavor,
        phase_re = phase_re,
        participant_re = participant_re,
        target = target,
        actual = actual,
        blanking = blanking
    )

"""

Notes for improvemenet:
- End goal: give user multiple ways to determine accuracy

"""
