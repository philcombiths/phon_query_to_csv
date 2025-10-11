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

    ft = pp.FeatureTable()

    t_seg = pp.word_fts(target)[0]
    a_seg = pp.word_fts(actual)[0]

    if t_seg['voi'] == a_seg['voi']:
        score = get_place_distance(t_seg, a_seg) + get_manner_distance(t_seg, a_seg) + 2

        return score / 7

    return 1;

def get_place_distance(t_seg, a_seg):
    """
    Helper function of get_score to calculate distance rating for place of articulation.

    Args:
        t_seg (Segment): The distinctive features of the IPA Target.
        a_seg (Segment): The distinctive features of the IPA Actual.

    Returns:
        (int): The distance rating, from 0 to 2.
    """

    # cg, ant, cor, distr, lab

    # Labials               [+ant][-cor][+lab]
    # Coronals              [+/-ant][+cor]
    # Dorsals               [-ant][-cor][-lo][+hi/back]
    # Radical               [-ant][-cor][-hi][+lo][+back]
    # Glottal               [-ant][-cor][-hi][-lo][-back]

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

    fts_to_check = ['cor', 'ant', 'distr', 'lab', 'hi', 'lo', 'back']

    for ft in fts_to_check:
        if t_seg[ft] == a_seg[ft]:
            next

        if ft == 'son':
            return 0;

        return 1;

    return 2;

def get_manner_distance(t_seg, a_seg):
    """
    Helper function of get_score to calculate distance rating for manner of articulation.

    Args:
        t_seg (Segment): The distinctive features of the IPA Target.
        a_seg (Segment): The distinctive features of the IPA Actual.

    Returns:
        (int): The distance rating, from 0 to 2.
    """

    # Obstruent             [-son]
    # Sonorant              [+son]

    # Nasal                 [+son][+cons][-cont][+nas]
    # Plosive               [-son][+cons][-cont][-nas]  [-delrel]
    # Affricate             [-son][+cons][-cont][-nas]  [+delrel]
    # Fricative             [-son][+cons][+cont][-nas]  [-lat]
    # L. Fricative          [-son][+cons][+cont][-nas]  [+lat]
    # Approximant           [+son][-cons][+cont][-nas]  [-lat]
    # L. Approximant        [+son][-cons][+cont][-nas]  [+lat]
    # Trill                 [+son][+cons][+cont][-nas]
    # Tap / Flap            [+son][+cons][-cont][-nas]

    fts_to_check = ['son', 'cons', 'cont', 'nas', 'delrel', 'lat']

    for ft in fts_to_check:
        if t_seg[ft] == a_seg[ft]:
            next

        if ft == 'son':
            return 0;

        return 1;

    return 2;
