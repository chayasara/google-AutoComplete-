import build_tree as bt
import autocomplete as ac
import json


def get_search_term(message):
    return input(message)


def read_data():
    trie_file = open("trie.json")
    data = json.load(trie_file)
    trie_file.close()
    return data[1]['trie'], data[0]['strings']


def raw_string(string):
    return ''.join([c for c in string if c.isalnum()]).lower()


if __name__ == "__main__":
    trie, strings = read_data()
    term = get_search_term("start searching: \n")

    while True:
        while term[-1] == "#":
            term = get_search_term("start searching: \n")
        result = ac.autocomplete(raw_string(term), trie, strings)
        for res in result:
            print("\033[91m {}\033[00m" .format(f"{res.completed_sentence} ({res.source_text}) score: {res.score} offset: {res.offset}"))
        if term[-1] == "#":
            term = get_search_term("start searching: \n")
        else:
            term = term + get_search_term(term)
