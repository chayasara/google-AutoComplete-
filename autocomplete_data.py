from dataclasses import dataclass


@dataclass
class AutoCompleteData:
    completed_sentence: str
    source_text: str
    offset: int
    score: int

    def __init__(self, completed_sentence, source_text, offset, score):
        self.completed_sentence = completed_sentence
        self.source_text = source_text
        self.offset = offset
        self.score = score

    def print(self):
        print(f"\033[94m {f'{self.completed_sentence} ({self.source_text})'}\033[00m", end='')
        print(f"\033[95m {f'score: {self.score} offset: {self.offset}'}\033[00m")
