from dataclasses import dataclass
from offline import get_line


@dataclass
class AutoCompleteData:
    completed_sentence: str
    source_text: str
    offset: int
    score: int

    def __init__(self, source: str, line: int, score: int):
        self.completed_sentence = get_line(source, line)
        self.source_text = source
        self.offset = line
        self.score = score
