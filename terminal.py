import sys

CSI = "\x1b["


def clear() -> None:
    sys.stdout.write(f"{CSI}2J{CSI}H")
    sys.stdout.flush()


def hide_cursor() -> None:
    sys.stdout.write(f"{CSI}?25l")
    sys.stdout.flush()


def show_cursor() -> None:
    sys.stdout.write(f"{CSI}?25h")
    sys.stdout.flush()
