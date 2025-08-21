from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from random import shuffle

WORDLIST = Path("WORDS.txt").read_text(encoding="utf-8").split()


@dataclass
class Word:
    letters: str
    guessed: bool = False
    guesser: str = ""


@dataclass
class Game:
    letters: list[str] = field(default_factory=list)
    words: list[Word] = field(default_factory=list)
    scores: defaultdict = field(default_factory=lambda: defaultdict(int))
    active: bool = False

    def pick_random_word(self, min_length=5):
        shuffle(WORDLIST)
        for word in WORDLIST:
            if len(word) >= min_length:
                self.set_word(word)
                return

    def set_word(self, s: str):
        self.letters = list(s)
        shuffle(self.letters)
        letter_counts = Counter(s)
        self.words = [Word(letters=word) for word in WORDLIST if Counter(word) <= letter_counts]
        self.words.sort(key=lambda w: (len(w.letters), w.letters))
        self.active = True

    def guess(self, player: str, guess: str):
        guess = guess.lower().strip()
        if not self.active:
            return
        for word in self.words:
            if not word.guessed and word.letters == guess:
                word.guessed = True
                word.guesser = player
                self.scores[player] += len(guess)

    def end_round(self):
        self.active = False

    def is_round_complete(self) -> bool:
        return all(word.guessed for word in self.words)
