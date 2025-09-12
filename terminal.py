import sys

CSI = "\x1b["
ERASE_REST_OF_LINE = f"{CSI}K"


def clear() -> None:
    sys.stdout.write(f"{CSI}2J{CSI}H")
    sys.stdout.flush()


def move_cursor_home() -> None:
    sys.stdout.write(f"{CSI}H")
    sys.stdout.flush()


def hide_cursor() -> None:
    sys.stdout.write(f"{CSI}?25l")
    sys.stdout.flush()


def show_cursor() -> None:
    sys.stdout.write(f"{CSI}?25h")
    sys.stdout.flush()
