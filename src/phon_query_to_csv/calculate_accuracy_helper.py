import panphon as pp

def get_score(target, actual):
    """
    Determine a more detailed scoring of accuracy of IPA Actual with resepct to IPA Target.
    
    Args:
        target (str): The IPA Target.
        actual (str): The IPA Actual.
        
    Returns:
        (float): The detailed score of accuracy.
    """

    f_table = pp.FeatureTable()

    t_seg = f_table.word_fts(target)[0]
    a_seg = f_table.word_fts(actual)[0]

    ctgs = [['blb', 'lbd', 'dnt', 'alv', 'plv', 'rtf', 'plt', 'vlr', 'uvl', 'phr', 'glt'],
            ['nas', 'plo', 'aff', 'fri', 'lfr', 'app', 'lap', 'tri', 'tfp']]
    dists = {
        'plcs' : {
            'blb': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'lbd': [1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            'dnt': [2, 1, 0, 1, 2, 3, 4, 5, 6, 7, 8],
            'alv': [3, 2, 1, 0, 1, 2, 3, 4, 5, 6, 7],
            'plv': [4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 6],
            'rtf': [5, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5],
            'plt': [6, 5, 4, 3, 2, 1, 0, 1, 2, 3, 4],
            'vlr': [7, 6, 5, 4, 3, 2, 1, 0, 1, 2, 3],
            'uvl': [8, 7, 6, 5, 4, 3, 2, 1, 0, 1, 2],
            'phr': [9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 1],
            'glt': [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        },
        'mans' : {
            'nas': [0, 1, 2, 3, 3, 3, 3, 2, 1],
            'plo': [1, 0, 1, 2, 2, 3, 3, 3, 2],
            'aff': [2, 1, 0, 1, 1, 2, 2, 3, 3],
            'fri': [3, 2, 1, 0, 1, 1, 2, 2, 3],
            'lfr': [3, 2, 1, 1, 0, 2, 1, 2, 3],
            'app': [3, 3, 2, 1, 2, 0, 1, 1, 2],
            'lap': [3, 3, 2, 2, 1, 1, 0, 1, 2],
            'tri': [2, 3, 3, 2, 2, 1, 1, 0, 1],
            'tfp': [1, 2, 3, 3, 3, 2, 2, 1, 0]
        }
    }

    if t_seg['voi'] == a_seg['voi']:
        plc_dist = get_distance(ctgs, dists['plcs'], get_place, t_seg, a_seg)
        man_dist = get_distance(ctgs, dists['mans'], get_manner, t_seg, a_seg)

        return;

    return;

def get_distance(ctgs, dists, get_art, t_seg, a_seg):
    t_ctg = get_art(t_seg)
    a_ctg = get_art(a_seg)
        
    return dists[t_ctg][ctgs.index(a_ctg)]
    
def get_place(seg):
    """
    Helper function of get_place_distance to determine place of articulation.

    Args:
        seg (Segment): The distinctive features of a given phone.

    Returns:
        (str): The place of articulation.
    """

    # Bilabial              [+ant][-cor][?]
    # Labiodental           [+ant][-cor][?]
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

    # Nasal                 [+son][+cons][-cont][+nas]
    # Plosive               [-son][+cons][-cont][-delrel]
    # Affricate             [-son][+cons][-cont][+delrel]
    # Fricative             [-son][+cons][+cont][-lat]
    # L. Fricative          [-son][+cons][+cont][+lat]
    # Approximant           [+son][-cons][+cont][-lat]
    # L. Approximant        [+son][-cons][+cont][+lat]
    # Trill                 [+son][+cons][+cont]
    # Tap / Flap            [+son][+cons][-cont][-nas]

    if seg.match({'son': -1, 'cons': 1, 'cont': -1}):
        return 'aff' if seg.match({'delrel': 1}) else 'plo'

    if seg.match({'son': -1, 'cons': 1, 'cont': 1}):
        return 'lfr' if seg.match({'lat': 1}) else 'fri'
    
    if seg.match({'son': 1, 'cons': -1, 'cont': 1}):
        return 'lap' if seg.match({'lat': 1}) else 'app'
    
    if seg.match({'son': 1, 'cons': 1, 'cont': -1}):
        return 'nas' if seg.match({'nas': 1}) else 'tfp'
    
    return 'tri'
