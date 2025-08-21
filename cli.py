from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass
class CommandLineOptions:
    channel: str | None = None
    round_duration: float = 120.0
    end_screen_duration: float = 10.0
    word: str | None = None
    show_title: bool = True
    min_words: int = 1
    max_words: int = 200
    longest_word_length_minimum: int = 5

    @staticmethod
    def parse(args: list[str]) -> CommandLineOptions:
        options = CommandLineOptions()
        ap = argparse.ArgumentParser()
        ap.add_argument("-c", "--channel", metavar="TWITCH_CHANNEL_NAME", type=str,
            help="choose a twitch.tv channel to play on")
        ap.add_argument("-w", "--word", metavar="LONGEST_HIDDEN_WORD", type=str,
            help="overrides the hidden word for first round")
        ap.add_argument("--round-duration", metavar="SECONDS", type=float,
            help=f"duration of the guessing phase in seconds (default: {options.round_duration})")
        ap.add_argument("--end-screen-duration", metavar="SECONDS", type=float,
            help="how long to show the leaderboard between rounds in seconds"
                f" (default: {options.end_screen_duration})")
        ap.add_argument("--show-title", action=argparse.BooleanOptionalAction,
            help="hide/show the title bar")
        ap.add_argument("--longest-word-length-minimum", metavar="LENGTH", type=int,
            help="set minimum length for the longest hidden word"
                f" (default: {options.longest_word_length_minimum})")
        ap.add_argument("--min-words", metavar="COUNT", type=int,
            help=f"set minimum number of words per round (default: {options.min_words})")
        ap.add_argument("--max-words", metavar="COUNT", type=int,
            help=f"set maximum number of words per round (default: {options.max_words})")
        return ap.parse_args(args, namespace=options)
