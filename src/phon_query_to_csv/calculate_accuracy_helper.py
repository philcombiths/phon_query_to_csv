import re
import panphon as pp

def get_accuracy(alignment, analysis):
    """
    Determines a more detailed scoring of accuracy of IPA Actual with respect to IPA Target

    Args:
        alignment (str): Each phone of target paired with their respective realization
        analysis (str): Syllable category of the phones being analyzed

    Returns:
        (float): The detailed score of accuracy, to be interpreted as a percentage
    """
    score = 0
    t_len = 0

    f_table = pp.FeatureTable()

    target = []
    actual = []

    phones = re.split(r'[:↔,]', alignment)[0::2]

    for p in range(len(phones)):
        seg = None
        
        if phones[p] != '∅':
            seg = f_table.word_fts(phones[p])[0]

        if p % 2:
            actual.append(seg)
        else:
            target.append(seg)

            if seg != None:
                t_len += 1

    score = 0

    for p in range(len(target)):
        score += score_pair(target[p], actual[p], analysis, phones[p * 2], phones[(p * 2) + 1])

    return score / (t_len * 15)

def score_pair(target, actual, analysis, t_phone, a_phone):
    """
    Gets the distance between two different primary articulations
    
    Args:
        target (<Segment>): Phon segment of the target phone
        actual (<Segment>): Phon segment of the actual phone
        analysis (string): Type of analysis being examined
        t_phone (string): Target phone in pair
        a_phone (string): Actual phone in pair
        
    Returns:
        (float): The distance between the two primary articulations
    """

    p_score = 0

    if target == None:
        p_score -= 1

    if target != None and actual != None:
        if analysis == 'Nucleus':
            p_score = score_vowels(target, actual)
        else:
            p_score = score_consonants(target, actual)
        
        if p_score == 15 and t_phone != a_phone:
            p_score -= 1
    
    print(p_score)

    return p_score

def score_consonants(target, actual):
    """
    Calculates the accuracy of a single actual phone with resepct to its paired target phone
    
    Args:
        target (<Segment>): Phon segment of the target phone
        actual (<Segment>): Phon segment of the actual phone
        
    Returns:
        score (float): The detailed score of accuracy
    """

    plcs = ['blb', 'lbd', 'dnt', 'alv', 'plv', 'rtf', 'plt', 'vlr', 'uvl', 'phr', 'glt']
    mans = ['fri', 'lfr', 'aff', 'plo', 'nas', 'ttf', 'lap', 'app']

    score = 15

    # Check for voicing
    if target['voi'] != actual['voi']:
        score -= 1

    # Check for place and manner of articulation
    score -= get_distance(plcs, get_place, target, actual)
    score -= get_distance(mans, get_manner, target, actual)

    return score;

def score_vowels(target, actual):
    return

def get_distance(arts, get_art, t_seg, a_seg):
    """
    Gets the distance between two different primary articulations
    
    Args:
        arts (list): Primary articulations to be examined
        get_art (method): Helper method used for getting the primary articulation
        t_seg (<Segment>): Phon segment of the target phone
        a_seg (<Segment>): Phon segment of the actual phone
        
    Returns:
        dist (float): The distance between the two primary articulations
    """

    t_art = get_art(t_seg)
    a_art = get_art(a_seg)

    dist = abs(arts.index(t_art) - arts.index(a_art))
        
    return dist
    
def get_place(seg):
    """
    Helper function of get_place_distance to determine place of articulation.

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
    
    if seg.match({'ant': 1, 'cor': -1}):
        return 'lbd' if seg.match({'strid': 1}) or seg.match({'delrel': 0}) else 'blb'

    if seg.match({'ant': 1, 'cor': 1}):
        return 'dnt' if seg.match({'distr': 1}) else 'alv'
    
    if seg.match({'ant': -1, 'cor': 1}):
        return 'plv' if seg.match({'distr': 1}) else 'rtf'
    
    if seg.match({'hi': 1}):
        return 'plt' if seg.match({'back': -1}) else 'vlr'
    
    if seg.match({'back': 1}):
        return 'phr' if seg.match({'lo': 1}) else 'uvl'
    
    return 'glt'

def get_manner(seg):
    """
    Helper function of get_manner_distance to determine manner of articulation.

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
    # Tap / Flap            [+son][+cons][+cont][0delrel][?]
    # Trill                 [+son][+cons][+cont][0delrel][?]
    # L. Approximant        [+son][+cons][+cont][-delrel]
    # Approximant           [+son][-cons][+cont][-delrel]

    if seg.match({'son': -1, 'cons': 1, 'cont': 1}):
        return 'lfr' if seg.match({'delrel': 1}) else 'fri'
    
    if seg.match({'son': -1, 'cons': 1, 'cont': -1}):
        return 'aff' if seg.match({'delrel': 1}) else 'plo'
    
    if seg.match({'son': 1, 'cons': -1, 'delrel': -1}):
        return 'lap' if seg.match({'cons': 1}) else 'app'
    
    if seg.match({'son': 1, 'cons': -1, 'delrel': 0}):
        return 'ttf'
    
    return 'nas'

# Example usage for testing
if __name__ == "__main__":
    directory = ''
    print(get_accuracy("∅:L↔s:L,p:O↔p:O,r:O↔∅:O", "Onset and Adjunct"))
