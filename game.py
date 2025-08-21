from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from random import shuffle

WORDLIST = Path("WORDS.txt").read_text(encoding="utf-8").split()


def words_for_letters(letters: Sequence[str]) -> list[str]:
    letter_counts = Counter(letters)
    return [word for word in WORDLIST if Counter(word) <= letter_counts]


@dataclass
class Word:
    letters: str
    guessed: bool = False
    guesser: str = ""


@dataclass
class Game:
    letters: list[str] = field(default_factory=list)
    words: list[Word] = field(default_factory=list)
    scores: Counter[str] = field(default_factory=Counter)
    active: bool = False

    def pick_random_word(
        self, *, min_length: int = 5, min_words: int = 1, max_words: int = 9001
    ) -> None:
        shuffle(WORDLIST)
        for word in WORDLIST:
            if min_length <= len(word) and min_words <= len(words_for_letters(word)) <= max_words:
                self.set_word(word)
                return
        error = f"No words matching given criteria ({min_length=} and {min_words=}) in the word list!"
        raise ValueError(error)

    def set_word(self, word: str) -> None:
        word = word.lower()
        self.letters = list(word)
        shuffle(self.letters)
        self.words = [Word(letters=w) for w in {word, *words_for_letters(self.letters)}]
        self.words.sort(key=lambda w: (len(w.letters), w.letters))
        self.active = True

    def guess(self, player: str, guess: str) -> None:
        guess = guess.lower().strip()
        if not self.active:
            return
        for word in self.words:
            if not word.guessed and word.letters == guess:
                word.guessed = True
                word.guesser = player
                self.scores[player] += len(guess)

    def end_round(self) -> None:
        self.active = False

    def is_round_complete(self) -> bool:
        return all(word.guessed for word in self.words)
