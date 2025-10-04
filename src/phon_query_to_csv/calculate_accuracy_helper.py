import panphon as pp

def get_score(target, actual):
    """
    Determine a more detailed scoring of accuracy of IPA Actual with resepct to IPA Target.
    
    Args:
        target (str): The IPA Target.
        actual (str): The IPA Actual.
        
    Returns:
        score (float): The detailed score of accuracy.
    """

    ft = pp.FeatureTable()
    score = 1

    t_segment = pp.word_fts(target)[0]
    a_segment = pp.word_fts(actual)[0]

    distances = [0, 0, 0]
    
    # if target-voice

    score -= 1

    # if
    #   near-place AND near-manner or
    #   target-place AND distal-manner or
    #   distal-place AND target-manner

    score += 1

