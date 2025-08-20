import time
from itertools import batched

import twitchbot
from game import Game

ROUND_LENGTH_SECONDS = 120.0


def clear_terminal():
    print(end="\x1b[2J\x1b[H")


def render_scores(game: Game):
    leaderboard = list(game.scores.items())
    leaderboard.sort(key=lambda p: p[1], reverse=True)
    print("LEADERBOARD:")
    for rank, (player, score) in enumerate(leaderboard[:10], 1):
        print(f"{rank}. {player:12s} {score}")


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


def poll_guesses(bot, game):
    for msg in bot.poll(timeout_seconds=1.0):
        if isinstance(msg, twitchbot.PrivMsg):
            # ts = datetime.datetime.now()
            # print(f"{msg.channel:10s} [{ts:%H:%M:%S}] <{msg.sender}> {msg.msg}")
            game.guess(msg.sender, msg.msg)


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
    round_start = time.time()
    game.pick_random_word()
    clear_terminal()
    render(game)

    while True:
        if local_game:
            guess = input("Your guess: ")
            time_elapsed = time.time() - round_start
            time_remaining = ROUND_LENGTH_SECONDS - time_elapsed
            if time_remaining >= 0:
                game.guess("You", guess)
        else:
            try:
                poll_guesses(bot, game)
            except ConnectionError as exc:
                print(exc)
                break
            except KeyboardInterrupt:
                bot.disconnect()
                raise
            except Exception:
                print("An exception was raised, attempting to disconnect...")
                bot.disconnect()
                raise

        time_elapsed = time.time() - round_start
        time_remaining = ROUND_LENGTH_SECONDS - time_elapsed

        clear_terminal()
        if game.is_round_complete() or time_remaining < 0:
            game.end_round()
            render(game)
            render_scores(game)
            if local_game:
                input("Press Enter to begin next round!")
            else:
                print("Next round begins automatically in 10 seconds...")
                time.sleep(10)
                bot.poll(timeout_seconds=0.1)
            game.pick_random_word()
            round_start = time.time()
            clear_terminal()
            render(game)
        else:
            print(f"TIME REMAINING: {time_remaining:.0f}s")
            render(game)
    print("Disconnected.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGG!")
