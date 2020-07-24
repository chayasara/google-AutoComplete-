from python.autocomplete_data import AutoCompleteData

# max_matching_characters = 50
num_suggestions = 5


# ----------------score_functions--------------


def prefect_match_score(term):
    return len(term) * 2


def replacement_score(term, index):
    negative_scores = {0: 5, 1: 4, 2: 3, 3: 2}
    negative_score = negative_scores[index] if index in negative_scores else 1
    return (index + len(term) - 1) * 2 - negative_score


def remove_add_letter_score(term, index):
    negative_scores = {0: 10, 1: 8, 2: 6, 3: 4}
    negative_score = negative_scores[index] if index in negative_scores else 2
    return (index + len(term)) * 2 - negative_score


# --------------AutocompleteData functions------------


def calc_offset(term, sentence):
    sentence = ''.join(c for c in sentence if c.isalnum()).lower()
    return sentence.find(term)


def create_autocomplete_data(matches):
    res = []
    for m in matches:
        res.append(AutoCompleteData(m['string'], m['filename'], m['offset'], m['score']))
    return res


# ----------------match functions--------------------

# ----helper functions----


def smaller_strings(matches):
    return sorted(matches, key=lambda m: m['string'])[:num_suggestions]


def best_score_for_same_id(matches):
    matches_ids = {}
    for match in matches:
        if match['id'] in matches_ids:
            if match['score'] > matches_ids[match['id']]['score']:
                matches_ids[match['id']] = match
        else:
            matches_ids[match['id']] = match
    return list(matches_ids.values())


def highest_scores(matches):
    largest = []
    for i in range(min(num_suggestions, len(matches))):
        largest.append(max(matches, key=lambda match: match['score']))
        matches.remove(largest[-1])
    return largest


def update_score_heap(matches, new_matches, score):
    matches += [{'score': score,
                 'id': match['id'],
                 'offset': match['offset'],
                 'string': match['string'],
                 'filename': match['filename']} for match in new_matches]

    matches = best_score_for_same_id(matches)
    matches = highest_scores(matches)
    return matches


def replacement_letters(trie, search_term):
    return trie['next_letters'].keys() - [search_term[0]]


# -------match functions-----------


def get_perfect_matches(term, i, trie, strings, new_term=None):
    if not new_term:  # TODO leave out new_term and take care of index
        new_term = term

    cur = trie
    if term[i:] != '':
        for letter in term[i:]:
            if letter not in cur['next_letters']:
                if not cur['next_letters']:
                    break
                return None
            else:
                cur = cur['next_letters'][letter]

    return [dict(id=ID,
                 offset=calc_offset(new_term, strings[ID][0]),
                 string=strings[ID][0],
                 filename=strings[ID][1])
            for ID in cur['ids']]


def perfect_matches(term, trie, strings):
    matches = get_perfect_matches(term, 0, trie, strings)

    if not matches:
        return []

    score = prefect_match_score(term)
    for match in matches:
        match['score'] = score

    if len(matches) >= num_suggestions:
        matches = smaller_strings(matches)
        return create_autocomplete_data(matches)

    return matches


def replacement_matches(term, trie, index, matches, strings):
    result = matches
    score = replacement_score(term[index:], index)
    for letter in replacement_letters(trie, term[index:]):
        new_term = term[:index] + letter + term[index + 1:]
        matches = get_perfect_matches(term, index + 1, trie['next_letters'][letter], strings, new_term)
        if not matches:
            continue
        result = update_score_heap(result, matches, score)
    return result


def add_letter_matches(term, trie, index, matches, strings):
    score = remove_add_letter_score(term[index:], index)
    result = matches
    for letter in trie['next_letters']:
        new_term = term[:index] + letter + term[index:]
        matches = get_perfect_matches(term, index, trie['next_letters'][letter], strings, new_term)
        if not matches:
            continue
        result = update_score_heap(result, matches, score)
    return result


def remove_letter_matches(term, trie, index, matches, strings):
    score = remove_add_letter_score(term[index:], index)
    result = matches

    if term[index + 1:] == '':
        return result
    new_term = term[:index] + term[index + 1:]
    matches = get_perfect_matches(term, index + 1, trie, strings, new_term)
    if matches:
        result = update_score_heap(result, matches, score)

    return result


def find_matches(search_term, trie, strings, possible_matches):
    non_perfect_match_func = [replacement_matches, add_letter_matches, remove_letter_matches]
    cur = trie
    matches = possible_matches
    for index, letter in enumerate(search_term):
        for match_func in non_perfect_match_func:
            matches = match_func(search_term, cur, index, matches, strings)

        if letter in cur['next_letters']:
            cur = cur['next_letters'][letter]
        else:
            break
    return create_autocomplete_data(matches)


def autocomplete(search_term, trie, strings):
    res = perfect_matches(search_term, trie, strings)

    if len(res) < num_suggestions:
        res = find_matches(search_term, trie, strings, res)

    return sorted(res, key=lambda i: (i.score, -i.offset), reverse=True)
