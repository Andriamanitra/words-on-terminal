# WOT - Words On Terminal

WOT is a word guessing game that you can play with twitch.tv chat
(just like https://wos.gg/ but in the comfort of your own terminal)

## How to play:

You will need Python (3.12 or newer is required). There are no other dependencies!

You can run the game using [uv](https://docs.astral.sh/uv/):
```
uv run --python 3.13 -m wot
```
or an existing Python installation on your system:
```
python3 -m wot
```

When you run the game it will first ask for a twitch channel to connect to.
After providing a channel name the game begins immediately and you can start guessing in Twitch chat.
If you don't provide a channel name the game will ask for your guesses in the terminal instead.

Press Ctrl+c or Ctrl+d to quit.
