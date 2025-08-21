import time
from itertools import batched

import twitchbot
from game import Game


class RoundTimer:
    def __init__(self, round_duration_seconds=120.0):
        self.round_duration_seconds = round_duration_seconds
        self.start = time.time()

    def reset(self):
        self.start = time.time()

    def remaining_seconds(self) -> float:
        return self.round_duration_seconds - self.elapsed_seconds()

    def elapsed_seconds(self) -> float:
        return time.time() - self.start

    def expired(self) -> bool:
        return self.elapsed_seconds() >= self.round_duration_seconds


def clear_terminal():
    print(end="\x1b[2J\x1b[H")


def render(game: Game):
    print("LETTERS:", " ".join(letter.upper() for letter in game.letters))
    output_words = []
    for word in game.words:
        if word.guessed:
            output_words.append(f"{word.letters.upper()}  ({word.guesser})")
        elif not game.active:
            output_words.append(f"{word.letters.upper()}")
        else:
            output_words.append("".join("_" for _ in word.letters))
    for outs in batched(output_words, 3):
        print(" ", "   ".join(out.ljust(25) for out in outs))


def render_end_round(game: Game):
    found = sum(1 for word in game.words if word.guessed)
    print(f"You managed to find {found}/{len(game.words)} words! Good job!")
    render(game)
    if game.scores:
        print("\nLEADERBOARD:")
        for rank, (player, score) in enumerate(game.scores.most_common(10), 1):
            print(f"{rank}. {player:12s} {score}")
    print()


def poll_guesses(bot, game):
    for msg in bot.poll(timeout_seconds=1.0):
        if isinstance(msg, twitchbot.PrivMsg):
            # ts = datetime.datetime.now()
            # print(f"{msg.channel:10s} [{ts:%H:%M:%S}] <{msg.sender}> {msg.msg}")
            game.guess(msg.sender, msg.msg)


def end_round(game: Game):
    game.end_round()
    clear_terminal()
    render_end_round(game)


def main():
    channel = input("Which twitch.tv channel to connect to (leave empty to play locally)?\n> ")
    local_game = False
    if not channel:
        print("No channel selected, playing locally!")
        local_game = True
    else:
        bot = twitchbot.Bot()
        bot.connect()
        print("Connected!")
        bot.join(channel)

    time.sleep(1.0)
    game = Game()
    timer = RoundTimer(round_duration_seconds=120.0)
    game.pick_random_word()

    while True:
        clear_terminal()
        print(f"TIME REMAINING: {timer.remaining_seconds():.0f}s")
        render(game)
        if local_game:
            try:
                guess = input("Your guess: ")
            except (EOFError, KeyboardInterrupt):
                end_round(game)
                print("GG!")
                return
            else:
                game.guess("You", guess)
        else:
            try:
                poll_guesses(bot, game)
            except (EOFError, KeyboardInterrupt):
                bot.disconnect()
                end_round(game)
                print("GG!")
                return
            except ConnectionError:
                raise
            except Exception:
                print("An exception was raised, attempting to disconnect...")
                bot.disconnect()
                raise

        if game.is_round_complete() or timer.expired():
            end_round(game)
            if local_game:
                input("Press Enter to begin next round!")
            else:
                print("Next round begins automatically in 10 seconds...")
                time.sleep(10)
                bot.poll(timeout_seconds=0.1)
            game.pick_random_word()
            timer.reset()
    print("Disconnected.")


if __name__ == "__main__":
    main()
