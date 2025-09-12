from __future__ import annotations

import shutil
import sys
import time
from itertools import batched

import terminal
import twitchbot
from cli import CommandLineOptions
from game import Game


class RoundTimer:
    def __init__(self, round_duration_seconds: float = 120.0) -> None:
        self.round_duration_seconds = round_duration_seconds
        self.start = time.time()

    def reset(self) -> None:
        self.start = time.time()

    def remaining_seconds(self) -> float:
        return self.round_duration_seconds - self.elapsed_seconds()

    def elapsed_seconds(self) -> float:
        return time.time() - self.start

    def expired(self) -> bool:
        return self.elapsed_seconds() >= self.round_duration_seconds


def render_title(options: CommandLineOptions, status: str) -> None:
    if options.show_title:
        print(f":: words on terminal :: {status} ::{terminal.ERASE_REST_OF_LINE}")


def render(game: Game, time_remaining: float | None = None) -> None:
    columns = shutil.get_terminal_size().columns // 26

    letters = " ".join(letter.upper() for letter in game.letters)
    letters = f" Letters:  {letters}"
    if time_remaining is not None:
        sep = "\n" if columns <= 1 else " " * (columns * 26 - 25 - len(letters))
        print(letters, f"Time remaining: {time_remaining:.0f}s{terminal.ERASE_REST_OF_LINE}", sep=sep)
    else:
        print(f"{letters}{terminal.ERASE_REST_OF_LINE}")

    output_words = []
    for word in game.words:
        if word.guessed:
            output_words.append(f"{word.letters.upper()}  ({truncate_username(word.guesser)})")
        elif not game.active:
            output_words.append(f"{word.letters.upper()}")
        else:
            output_words.append("".join("_" for _ in word.letters))

    for outs in batched(output_words, columns):
        joined_words = "  ".join(out.ljust(24) for out in outs)
        print(f" {joined_words}{terminal.ERASE_REST_OF_LINE}")


def render_end_round(game: Game) -> None:
    found = sum(1 for word in game.words if word.guessed)
    render(game)
    print(f"You managed to find {found}/{len(game.words)} words! Good job!")
    if game.scores:
        print("\nLEADERBOARD:")
        for rank, (player, score) in enumerate(game.scores.most_common(10), 1):
            print(f"{rank}. {player:12s} {score}")
    print()


def play(game: Game, options: CommandLineOptions, connection: twitchbot.Bot | None = None) -> None:
    def start_round() -> None:
        timer.reset()
        game.pick_random_word(
            min_length=options.longest_word_length_minimum,
            min_words=options.min_words,
            max_words=options.max_words,
        )
        terminal.clear()

    timer = RoundTimer(options.round_duration)
    if options.word:
        game.set_word(options.word)
        options.word = None
    else:
        start_round()
    terminal.clear()

    if connection is None:
        status = "playing locally"
    else:
        status = f"playing on https://twitch.tv/{options.channel}"

    while True:
        terminal.move_cursor_home()
        render_title(options, status)
        render(game, timer.remaining_seconds())
        if connection is None:
            guess = input("Your guess: ")
            game.guess("You", guess)
        else:
            for msg in connection.poll(timeout_seconds=1.0):
                game.guess(msg.sender, msg.msg)

        if game.is_round_complete() or timer.expired():
            game.end_round()
            terminal.clear()
            render_title(options, status)
            render_end_round(game)
            if connection is None:
                input("Press Enter to begin next round!")
            else:
                delay = round(options.end_screen_duration)
                print(f"Next round begins automatically in {delay} seconds...")
                time.sleep(options.end_screen_duration)
                connection.poll(timeout_seconds=0.1)
            start_round()

def truncate_username(username, max_length=12):
    if len(username) <= max_length:
        return username
    
    last_char = username[-1]
    start_chars = 1
    
    while True:
        omitted_count = len(username) - start_chars - 1
        test_display = f"{username[:start_chars]}{omitted_count}{last_char}"
        
        if len(test_display) > max_length:
            start_chars -= 1
            omitted_count = len(username) - start_chars - 1
            return f"{username[:start_chars]}{omitted_count}{last_char}"
        elif omitted_count <= 0:
            return username
        else:
            start_chars += 1

def main() -> int:
    options = CommandLineOptions.parse(sys.argv[1:])
    if options.channel:
        if any(c != "_" and not c.isalnum() for c in options.channel):
            url = f"https://twitch.tv/{options.channel}"
            print(f"{url!r} is not a valid twitch channel!", file=sys.stderr)
            return 11
        connection = twitchbot.Bot()
        connection.connect()
        connection.join(options.channel)
        terminal.hide_cursor()
    else:
        connection = None

    game = Game()
    try:
        play(game, options, connection)
    except ConnectionError as exc:
        print(f"Disconnected due to {exc}", file=sys.stderr)
        connection = None
        return 21
    except (EOFError, KeyboardInterrupt):
        game.end_round()
        terminal.clear()
        render_title(options, "GAME OVER")
        render_end_round(game)
        print("GG!")
    finally:
        terminal.show_cursor()
        if connection is not None:
            connection.disconnect()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
