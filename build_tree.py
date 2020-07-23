import json
import os


def node(id):
    return{
            'ids': id if type(id) is list else [id],
            'next_letters': {}
            }


def insert_string_to_trie(root, string, id):
    cur = root
    for letter in string[:15]:
        if letter not in cur['next_letters']:
            cur['next_letters'][letter] = node(id)
        elif id not in cur['next_letters'][letter]['ids']:
            cur['next_letters'][letter]['ids'].append(id)
        cur = cur['next_letters'][letter]


def split_data(data, file_name):
    return [(string, file_name) for string in data]

def walk_in_file_tree():
    for root, dirs, files in os.walk('./nice_sentences'):
        for file in files:
            data = open(os.path.join(root, file),"r")
            yield data, file


def clean_words(words):
    return [''.join(e for e in word if e.isalnum()).lower() for word in words]


def insert_substrings_to_trie(trie, string, id):
    words = string.split(' ')
    words = clean_words(words)
    for i in range(len(words)):
        insert_string_to_trie(trie, ''.join(words[i:]), id)


def insert_lines_to_trie(root):
    id = 0
    mapped_data = []
    for data_file, file_name in walk_in_file_tree():
        lines = data_file.read().split("\n")
        for line in lines:
            mapped_data.append((line, file_name))
            insert_substrings_to_trie(root, line, id)
            id += 1
    root['ids'] = list(range(id))
    return mapped_data


def build_trie():
    root = node(0)
    mapped_data = insert_lines_to_trie(root)

    data_for_file = [{"strings": mapped_data}, {"trie": root}]

    with open("trie.json", "w") as f:
        json.dump(data_for_file, f)


if __name__ == "__main__":
    build_trie()