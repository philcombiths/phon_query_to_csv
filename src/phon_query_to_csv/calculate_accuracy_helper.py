import panphon as pp
import pandas as pd
import os
import unicodedata

VALID_NAN_POLICIES = {"max", "mid", "zero"}
RHOTIC_PHONES = {"r", "ɾ", "ɹ"}
PARAM_FEATURE_KEYS = {
    "place": ["ant", "cor", "distr", "hi", "lo", "back", "strid", "delrel"],
    "manner": ["son", "cons", "cont", "delrel"],
    "height": ["hi", "lo"]
}
PLACE_RULES = [
    ("blb", {"ant": 1, "cor": -1, "strid": -1}),
    ("blb", {"ant": 1, "cor": -1, "strid": 0}),
    ("blb", {"ant": 1, "cor": -1, "delrel": -1}),
    ("blb", {"ant": 1, "cor": -1, "delrel": 1}),
    ("lbd", {"ant": 1, "cor": -1, "strid": 1}),
    ("lbd", {"ant": 1, "cor": -1, "delrel": 0}),
    ("dnt", {"ant": 1, "cor": 1, "distr": 1}),
    ("alv", {"ant": 1, "cor": 1, "distr": -1}),
    ("plv", {"ant": -1, "cor": 1, "distr": 1}),
    ("rtf", {"ant": -1, "cor": 1, "distr": -1}),
    ("rtf", {"ant": -1, "cor": 1, "distr": 0}),
    ("plt", {"ant": -1, "cor": -1, "hi": 1, "lo": -1, "back": -1}),
    ("vlr", {"ant": -1, "cor": -1, "hi": 1, "lo": -1, "back": 0}),
    ("vlr", {"ant": -1, "cor": -1, "hi": 1, "lo": -1, "back": 1}),
    ("uvl", {"ant": -1, "cor": -1, "hi": -1, "lo": -1, "back": 1}),
    ("phr", {"ant": -1, "cor": -1, "hi": -1, "lo": 1, "back": 1}),
    ("glt", {"ant": -1, "cor": -1, "hi": -1, "lo": -1, "back": -1}),
]
MANNER_RULES = [
    ("fri", {"son": -1, "cons": 1, "cont": 1, "delrel": -1}),
    ("lfr", {"son": -1, "cons": 1, "cont": 1, "delrel": 1}),
    ("aff", {"son": -1, "cons": 1, "cont": -1, "delrel": 1}),
    ("plo", {"son": -1, "cons": 1, "cont": -1, "delrel": -1}),
    ("plo", {"son": 1, "cons": -1, "cont": -1, "delrel": -1}),
    ("nas", {"son": 1, "cons": 1, "cont": -1, "delrel": -1}),
    ("ttf", {"son": 1, "cons": 1, "cont": 1, "delrel": 0}),
    ("lap", {"son": 1, "cons": 1, "cont": 1, "delrel": -1}),
    ("app", {"son": 1, "cons": -1, "cont": 1, "delrel": -1}),
]
HEIGHT_RULES = [
    ("cls", {"hi": 1, "lo": -1}),
    ("mid", {"hi": -1, "lo": -1}),
    ("opn", {"hi": -1, "lo": 1}),
]

def _feature_snapshot(seg, art_name):
    if seg is None:
        return {}

    keys = PARAM_FEATURE_KEYS.get(art_name, [])
    snapshot = {}

    for key in keys:
        snapshot[key] = seg[key]

    return snapshot

def _classify_with_fallback(seg, rules, parameter, phone, role, fallback_events):
    for label, cond in rules:
        if seg.match(cond):
            return label

    best = None

    for label, cond in rules:
        compared = 0
        mismatches = 0
        compared_features = []

        for feat, expected in cond.items():
            actual = seg[feat]

            if actual == 0:
                continue

            compared += 1
            compared_features.append(feat)

            if actual != expected:
                mismatches += 1

        if compared == 0:
            continue

        candidate = {
            "label": label,
            "rule": cond,
            "compared": compared,
            "mismatches": mismatches,
            "compared_features": compared_features
        }

        if (
            best is None
            or candidate["mismatches"] < best["mismatches"]
            or (
                candidate["mismatches"] == best["mismatches"]
                and candidate["compared"] > best["compared"]
            )
        ):
            best = candidate

    if best is None:
        if fallback_events is not None:
            fallback_events.append({
                "event_type": "fallback_unresolved",
                "parameter": parameter,
                "phone": phone,
                "role": role,
                "features": _feature_snapshot(seg, parameter)
            })
        return "nan"

    if fallback_events is not None:
        fallback_events.append({
            "event_type": "fallback_used",
            "parameter": parameter,
            "phone": phone,
            "role": role,
            "selected_label": best["label"],
            "mismatches": best["mismatches"],
            "compared": best["compared"],
            "compared_features": best["compared_features"],
            "rule": best["rule"],
            "features": _feature_snapshot(seg, parameter)
        })

    return best["label"]

def _log_manual_override(fallback_events, parameter, phone, role, selected_label, reason, seg):
    if fallback_events is None:
        return

    fallback_events.append({
        "event_type": "manual_override",
        "parameter": parameter,
        "phone": phone,
        "role": role,
        "selected_label": selected_label,
        "reason": reason,
        "features": _feature_snapshot(seg, parameter)
    })

def get_accuracy(alignment, analysis, nan_policy="max", return_debug=False):
    """
    Determines a more detailed scoring of accuracy of IPA Actual with respect to IPA Target

    Args:
        alignment (str): Each phone of target paired with their respective realization
        analysis (str): Syllable category of the phones being analyzed
        nan_policy (str): Policy for handling unclassified articulations ('nan').
            Supported values: 'max', 'mid', 'zero'
        return_debug (bool): If True, returns a third value with debug details
            (nan_events and fallback_events).

    Returns:
        (float): The detailed score of accuracy, to be interpreted as a percentage
    """

    if not isinstance(alignment, str):
        if return_debug:
            return -1, "No alignment!", {"nan_events": [], "fallback_events": []}
        return -1, "No alignment!"

    if nan_policy not in VALID_NAN_POLICIES:
        if return_debug:
            return -1, f"Invalid nan_policy '{nan_policy}'. Use one of: max, mid, zero", {"nan_events": [], "fallback_events": []}
        return -1, f"Invalid nan_policy '{nan_policy}'. Use one of: max, mid, zero"

    score = 0
    t_len = 0

    f_table = pp.FeatureTable()

    target = []
    actual = []

    # Retrieve phones from alignment, convert to panphon segments, and place in parallel lists
    phones = get_phones(alignment)

    invalid_phones = []

    for p in range(len(phones)):
        seg = None
        phone = phones[p]

        if phone != '∅':
            segs = f_table.word_fts(phone)

            if segs:
                seg = segs[0]
            else:
                invalid_phones.append(phone)

        if p % 2:
            actual.append(seg)
        else:
            target.append(seg)

            if seg != None:
                t_len += 1

    # Score pair by pair, sum the scores, and divide it according to summed max possible scores
    score = 0
    nan_events = []
    fallback_events = []

    for p in range(len(target)):
        score += score_pair(
            target[p],
            actual[p],
            analysis,
            phones[p * 2],
            phones[(p * 2) + 1],
            nan_policy=nan_policy,
            nan_events=nan_events,
            fallback_events=fallback_events
        )

    if invalid_phones:
        unique_invalid = sorted(set(invalid_phones))
        if return_debug:
            return -1, "Unrecognized IPA phone(s): " + ", ".join(unique_invalid), {"nan_events": nan_events, "fallback_events": fallback_events}
        return -1, "Unrecognized IPA phone(s): " + ", ".join(unique_invalid)

    if score < 0:
        if return_debug:
            return -1, "Invalid alignment!", {"nan_events": nan_events, "fallback_events": fallback_events}
        return -1, "Invalid alignment!"

    if t_len == 0:
        if return_debug:
            return -1, "No valid target phones!", {"nan_events": nan_events, "fallback_events": fallback_events}
        return -1, "No valid target phones!"

    if analysis == 'Nucleus':
        accuracy = score / (t_len * 5)
        if return_debug:
            return accuracy, "", {"nan_events": nan_events, "fallback_events": fallback_events}
        return accuracy, ""

    accuracy = score / (t_len * 17)
    if return_debug:
        return accuracy, "", {"nan_events": nan_events, "fallback_events": fallback_events}
    return accuracy, ""

def get_phones(alignment):
    phones = []

    for pair in alignment.split(','):
        for phone in pair.split('↔'):
            phones.append(filter_special_chars(phone.split(':')[0]))

    return phones

def filter_special_chars(phone):
    phone = phone.replace('g', 'ɡ')

    phone = phone.replace('ʦ', 't͡s')
    phone = phone.replace('ʣ', 'd͡z')
    phone = phone.replace('ʧ', 't͡ʃ')
    phone = phone.replace('ʤ', 'd͡ʒ')
    phone = phone.replace('ʪ', 'ɬ')
    phone = phone.replace('ʫ', 'ɮ')

    phone = phone.replace('ʡ', 'ʔ̟')
    phone = phone.replace('ʜ', 'ʁ̠̥')
    phone = phone.replace('ʢ', 'ʀ̠')

    return phone

# If needed for special character accomidation failure
def filter_base_helper(phone, old_base, new_base):
    result = []

    for c in phone:
        # Decompose character
        decomposed = unicodedata.normalize("NFD", c)

        base = decomposed[0]
        combining = decomposed[1:]

        if base == old_base:
            base = new_base

        # Recompose
        result.append(unicodedata.normalize("NFC", base + combining))

    return "".join(result)

def score_pair(target, actual, analysis, t_phone, a_phone, nan_policy="max", nan_events=None, fallback_events=None):
    """
    Gets the distance between two different primary articulations
    
    Args:
        target (<Segment>): Phon segment of the target phone
        actual (<Segment>): Phon segment of the actual phone
        analysis (string): Type of analysis being examined
        t_phone (string): Target phone in pair
        a_phone (string): Actual phone in pair
        nan_policy (str): Policy for handling unclassified articulations ('nan').
            Supported values: 'max', 'mid', 'zero'
            max: Unclassified features receive the maximum distance penalty [len(arts) - 1]
            mid: Unclassified features receive a mid-distance penalty [(len(arts)-1) / 2]
            zero: Unclassified features receive no penalty [0]
        
    Returns:
        (float): The distance between the two primary articulations
    """

    p_score = 0

    # Subtract a point if there is no target (inserted sound in actual)
    if target == None:
        p_score -= 1

    # Score according to analysis type.
    if target != None and actual != None:
        if analysis == 'Nucleus':
            p_score = score_vowels(
                target,
                actual,
                nan_policy=nan_policy,
                t_phone=t_phone,
                a_phone=a_phone,
                nan_events=nan_events,
                fallback_events=fallback_events
            )
        else:
            p_score = score_consonants(
                target,
                actual,
                nan_policy=nan_policy,
                t_phone=t_phone,
                a_phone=a_phone,
                nan_events=nan_events,
                fallback_events=fallback_events
            )

        # Apply symbol mismatch penalty for any non-identical realized pair.
        if t_phone != a_phone:
            p_score -= 1

    return p_score

def score_consonants(target, actual, nan_policy="max", t_phone=None, a_phone=None, nan_events=None, fallback_events=None):
    """
    Calculates the accuracy of a single actual phone with resepct to its paired target phone
    
    Args:
        target (<Segment>): Phon segment of the target phone
        actual (<Segment>): Phon segment of the actual phone
        nan_policy (str): Policy for handling unclassified articulations ('nan').
            Supported values: 'max', 'mid', 'zero'
        
    Returns:
        score (float): The detailed score of accuracy
    """

    plcs = ['blb', 'lbd', 'dnt', 'alv', 'plv', 'rtf', 'plt', 'vlr', 'uvl', 'phr', 'glt']
    mans = ['fri', 'lfr', 'aff', 'plo', 'nas', 'ttf', 'lap', 'app']

    score = 17

    # Check for voicing
    if target['voi'] != actual['voi']:
        score -= 1

    # Check for place and manner of articulation
    score -= get_distance(
        plcs,
        get_place,
        target,
        actual,
        nan_policy=nan_policy,
        art_name="place",
        t_phone=t_phone,
        a_phone=a_phone,
        nan_events=nan_events,
        fallback_events=fallback_events
    )
    score -= get_distance(
        mans,
        get_manner,
        target,
        actual,
        nan_policy=nan_policy,
        art_name="manner",
        t_phone=t_phone,
        a_phone=a_phone,
        nan_events=nan_events,
        fallback_events=fallback_events
    )

    # Rhotic sub-manner penalty: distinguish trill contrasts within rhotics.
    if (
        t_phone in RHOTIC_PHONES
        and a_phone in RHOTIC_PHONES
        and target["trill"] != actual["trill"]
    ):
        score -= 1

    return score;

def score_vowels(target, actual, nan_policy="max", t_phone=None, a_phone=None, nan_events=None, fallback_events=None):
    """
    Calculates the accuracy of a single actual phone with resepct to its paired target phone
    
    Args:
        target (<Segment>): Phon segment of the target phone
        actual (<Segment>): Phon segment of the actual phone
        nan_policy (str): Policy for handling unclassified articulations ('nan').
            Supported values: 'max', 'mid', 'zero'
        
    Returns:
        score (float): The detailed score of accuracy
    """

    hts = ['cls', 'mid', 'opn']

    score = 5

    # Check for backness
    if target['back'] != actual['back']:
        score -= 1

    # Check for roundedness
    if target['round'] != actual['round']:
        score -= 1

    # Check for height
    score -= get_distance(
        hts,
        get_height,
        target,
        actual,
        nan_policy=nan_policy,
        art_name="height",
        t_phone=t_phone,
        a_phone=a_phone,
        nan_events=nan_events,
        fallback_events=fallback_events
    )

    return score

def get_distance(
    arts,
    get_art,
    t_seg,
    a_seg,
    nan_policy="max",
    art_name=None,
    t_phone=None,
    a_phone=None,
    nan_events=None,
    fallback_events=None
):
    """
    Gets the distance between two different primary articulations
    
    Args:
        arts (list): Primary articulations to be examined
        get_art (method): Helper method used for getting the primary articulation
        t_seg (<Segment>): Phon segment of the target phone
        a_seg (<Segment>): Phon segment of the actual phone
        nan_policy (str): Policy for handling unclassified articulations ('nan').
            Supported values: 'max', 'mid', 'zero'
        
    Returns:
        dist (float): The distance between the two primary articulations
    """

    t_art = get_art(
        t_seg,
        fallback_events=fallback_events,
        role="target",
        phone=t_phone
    )
    a_art = get_art(
        a_seg,
        fallback_events=fallback_events,
        role="actual",
        phone=a_phone
    )

    # Panphon frequently underspecifies some features as 0, which can make
    # our categorical mapper return 'nan'. Use bounded penalties so
    # substitutions still receive a graded score instead of being invalid.
    if t_art == 'nan' or a_art == 'nan':
        max_dist = len(arts) - 1
        if nan_policy == "zero":
            penalty = 0
        elif nan_policy == "mid":
            penalty = max_dist / 2
        else:
            penalty = max_dist

        if nan_events is not None:
            nan_events.append({
                "parameter": art_name,
                "target_phone": t_phone,
                "actual_phone": a_phone,
                "target_articulation": t_art,
                "actual_articulation": a_art,
                "target_features": _feature_snapshot(t_seg, art_name),
                "actual_features": _feature_snapshot(a_seg, art_name),
                "penalty": penalty,
                "nan_policy": nan_policy
            })

        return penalty

    dist = abs(arts.index(t_art) - arts.index(a_art))
        
    return dist
    
def get_height(seg, fallback_events=None, role=None, phone=None):
    """
    Helper function of get_distance to determine height.

    Args:
        seg (Segment): The distinctive features of a given phone.

    Returns:
        (str): The height
    """

    return _classify_with_fallback(
        seg,
        HEIGHT_RULES,
        parameter="height",
        phone=phone,
        role=role,
        fallback_events=fallback_events
    )

def get_place(seg, fallback_events=None, role=None, phone=None):
    """
    Helper function of get_distance to determine place of articulation.

    Args:
        seg (Segment): The distinctive features of a given phone.

    Returns:
        (str): The place of articulation.
    """

    # Bilabial              [+ant][-cor] & [-/0strid] or [-/+delrel]
    # Labiodental           [+ant][-cor] & [+strid] or [0delrel]
    # Dental                [+ant][+cor][+distr]
    # Alveolar              [+ant][+cor][-distr]
    # Postalveolar          [-ant][+cor][+distr]
    # Retroflex             [-ant][+cor][-/0distr]
    # Palatal               [-ant][-cor][+hi][-lo][-back]
    # Velar                 [-ant][-cor][+hi][-lo][+/0back]
    # Uvular                [-ant][-cor][-hi][-lo][+back]
    # Pharyngeal            [-ant][-cor][-hi][+lo][+back]
    # Glottal               [-ant][-cor][-hi][-lo][-back]

    # Manual rhotic override: keep rhotics in a shared coronal bucket so
    # /r ɾ ɹ/ are not treated as maximally distant due underspecification.
    if phone in RHOTIC_PHONES:
        _log_manual_override(
            fallback_events,
            parameter="place",
            phone=phone,
            role=role,
            selected_label="alv",
            reason="rhotic_place_override",
            seg=seg
        )
        return "alv"

    return _classify_with_fallback(
        seg,
        PLACE_RULES,
        parameter="place",
        phone=phone,
        role=role,
        fallback_events=fallback_events
    )

def get_manner(seg, fallback_events=None, role=None, phone=None):
    """
    Helper function of get_distance to determine manner of articulation.

    Args:
        seg (Segment): The distinctive features of a given phone.

    Returns:
        (str): The manner of articulation.
    """
        
    # Fricative             [-son][+cons][+cont][-delrel]
    # L. Fricative          [-son][+cons][+cont][+delrel]
    # Affricate             [-son][+cons][-cont][+delrel]
    # Plosive               [-son][+cons][-cont][-delrel]
    # Nasal                 [+son][+cons][-cont][-delrel]
    # Tap / Flap / Trill    [+son][+cons][+cont][0delrel]
    # L. Approximant        [+son][+cons][+cont][-delrel]
    # Approximant           [+son][-cons][+cont][-delrel]

    # Manual rhotic override: tap/trill rhotics stay ttf, approximant rhotic
    # maps to lap so rhotic substitutions remain close but not identical.
    if phone in {"r", "ɾ"}:
        _log_manual_override(
            fallback_events,
            parameter="manner",
            phone=phone,
            role=role,
            selected_label="ttf",
            reason="rhotic_manner_override_ttf",
            seg=seg
        )
        return "ttf"

    if phone == "ɹ":
        _log_manual_override(
            fallback_events,
            parameter="manner",
            phone=phone,
            role=role,
            selected_label="lap",
            reason="rhotic_manner_override_lap",
            seg=seg
        )
        return "lap"

    return _classify_with_fallback(
        seg,
        MANNER_RULES,
        parameter="manner",
        phone=phone,
        role=role,
        fallback_events=fallback_events
    )
