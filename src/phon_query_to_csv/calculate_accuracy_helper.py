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


def get_manner_distance(t_seg, a_seg):
    """
    Helper function of get_score to calculate distance rating for manner of articulation.

    Args:
        t_seg (Segment): The distinctive features of the IPA Target.
        a_seg (Segment): The distinctive features of the IPA Actual.

    Returns:
        (int): The distance rating, from 0 to 2.
    """

