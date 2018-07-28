def get_match_score(a, b):
    if (a['gender'] == b['gender'] or
            abs(a['age'] - b['age']) > 3 or
            a['city'] != b['city']):
        return 0

    score = 0
    for key in ['occupation', 'hobbies', 'music']:
        score += len(set(a[key]) & set(b[key]))
    return score
