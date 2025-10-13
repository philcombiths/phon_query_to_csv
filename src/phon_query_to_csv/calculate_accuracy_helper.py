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

    # Bilabial              [+ant][-cor]    [+lab][?]
    # Labiodental           [+ant][-cor]    [+lab][?]
    # Dental                [+ant][+cor]    [+distr]
    # Alveolar              [+ant][+cor]    [-distr]
    # Postalveolar          [-ant][+cor]    [+distr]
    # Retroflex             [-ant][+cor]    [-/0distr]
    # Palatal               [-ant][-cor]    [+hi][-lo][-back]
    # Velar                 [-ant][-cor]    [+hi][-lo][+/0back]
    # Uvular                [-ant][-cor]    [-hi][-lo][+back]
    # Pharyngeal            [-ant][-cor]    [-hi][+lo][+back]
    # Glottal               [-ant][-cor]    [-hi][-lo][-back]

    return;

def get_manner(seg):
    """
    Helper function of get_manner_distance to determine manner of articulation.

    Args:
        seg (Segment): The distinctive features of a given phone.

    Returns:
        (str): The manner of articulation.
    """

    # Nasal                 [+son][+cons][-cont][+nas]
    # Plosive               [-son][+cons][-cont][-nas][-delrel]
    # Affricate             [-son][+cons][-cont][-nas][+delrel]
    # Fricative             [-son][+cons][+cont][-nas][-lat]
    # L. Fricative          [-son][+cons][+cont][-nas][+lat]
    # Approximant           [+son][-cons][+cont][-nas][-lat]
    # L. Approximant        [+son][-cons][+cont][-nas][+lat]
    # Trill                 [+son][+cons][+cont][-nas]
    # Tap / Flap            [+son][+cons][-cont][-nas]

    if seg['son'] == 1:
        if seg['cons'] == 1:
            if seg['cont'] == 1:
                return 'tri'
            
            if seg['nas'] == 1:
                return 'nas'
            
            return 'tfp'
        
        if seg['lat'] == 1:
            return 'lap'
        
        return 'app'
    
    if seg['cont'] == 1:
        if seg['lat'] == 1:
            return 'lfr'
        
        return 'fri'
    
    if seg['delrel'] == 1:
        return 'aff'
    
    return 'plo'
