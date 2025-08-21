# WOT - Words On Terminal

WOT is a word guessing game that you can play with twitch.tv chat
(just like https://wos.gg/ but in the comfort of your own terminal)

## How to play:

You will need Python (3.12 or newer is required). There are no other dependencies!

Start by cloning the repository:
```
git clone https://github.com/Andriamanitra/words-on-terminal
cd words-on-terminal
```

You can then run the game using [uv](https://docs.astral.sh/uv/):
```
uv run -m wot --channel YOUR_TWITCH_CHANNEL
```
or an existing Python installation on your system:
```
python3 -m wot --channel YOUR_TWITCH_CHANNEL
```

The game begins immediately when you run the command, and you can start guessing in Twitch chat.
If you don't provide `--channel` argument the game will ask for your guesses in the terminal instead.
Check `--help` for all supported options.

Press Ctrl+c or Ctrl+d to quit.
