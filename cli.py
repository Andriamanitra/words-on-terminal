from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass
class CommandLineOptions:
    channel: str | None = None
    round_duration: float = 120.0
    end_screen_duration: float = 10.0
    show_title: bool = True

    @staticmethod
    def parse(args: list[str]) -> CommandLineOptions:
        ap = argparse.ArgumentParser()
        ap.add_argument("-c", "--channel", metavar="TWITCH_CHANNEL_NAME", type=str)
        ap.add_argument("--round-duration", metavar="SECONDS", type=float)
        ap.add_argument("--end-screen-duration", metavar="SECONDS", type=float)
        ap.add_argument("--show-title", action=argparse.BooleanOptionalAction)
        return ap.parse_args(args, namespace=CommandLineOptions())
