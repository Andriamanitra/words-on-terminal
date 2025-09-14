from __future__ import annotations

import socket
from collections.abc import Iterator
from dataclasses import dataclass


@dataclass
class Message:
    """
    The base class that should be able to handle all messages.
    Common message types like PRIVMSG can subclass this class to
    add extra functionality.
    """
    raw: str
    prefix: str | None
    command: str
    params: list[str]
    tags: dict[str, str]

    @staticmethod
    def parse_tags(rawmsg: str) -> tuple[dict[str, str], str]:
        tags = {}
        if rawmsg.startswith("@"):
            tags_str, _, rawmsg = rawmsg.partition(" ")
            for tag in tags_str.removeprefix("@").split(";"):
                name, _, value = tag.partition("=")
                tags[name] = value
        return tags, rawmsg

    @staticmethod
    def parse(rawmsg: str) -> Message:
        # the tags are only present if the user requested them by sending
        # "CAP REQ :twitch.tv/commands twitch.tv/tags"
        tags, rawmsg = Message.parse_tags(rawmsg.strip())
        # the rest of the message is parsed according to the rfc:
        # https://datatracker.ietf.org/doc/html/rfc1459#section-2.3
        if rawmsg.startswith(":"):
            prefix, _, rest = rawmsg.removeprefix(":").partition(" ")
        else:
            prefix = None
            rest = rawmsg
        command, _, params_str = rest.partition(" ")
        params_str, _, trailing = params_str.partition(" :")
        params = params_str.split()
        if trailing:
            params.append(trailing)

        if command == "PRIVMSG":
            return PrivMsg(rawmsg, prefix, command, params, tags)
        if command == "USERNOTICE":
            return UserNotice(rawmsg, prefix, command, params, tags)
        return Message(rawmsg, prefix, command, params, tags)


class UserNotice(Message):
    """
    Message type for subscriptions, raids, etc.
    docs: https://dev.twitch.tv/docs/irc/commands#usernotice
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel = self.params[0]
        self.system_msg = self.tags.get("system-msg", "").replace("\\s", " ")
        self.user_msg = ""
        if len(self.params) > 1:
            self.user_msg = self.params[1]

    def __str__(self) -> str:
        if self.user_msg:
            return f'{self.channel:10s} {self.system_msg} "{self.user_msg}"'
        return f"{self.channel:10s} {self.system_msg}"


class PrivMsg(Message):
    """
    Message type for chat messages sent to a channel
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        display_name = self.tags.get("display-name")
        if display_name:
            self.sender = display_name
        else:
            self.sender = self.prefix.partition("!")[0]
        self.msg = self.params[-1]
        self.channel = self.params[-2]


class Bot:
    def __init__(self, username="justinfan123"):
        # the username 'justinfan' followed by any number is a special
        # username that can be used to connect to twitch chat without
        # authenticating (read-only, it can't send any messages)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = username
        self.buffer = b""

    def connect(
            self,
            server="irc.twitch.tv",
            password="BLANK",
            port=6667,
            *,
            request_tags=True
    ):
        self.sock.connect((server, port))
        self.send(f"PASS {password}")
        self.send(f"NICK {self.username}")
        self.send(f"USER {self.username} 8 * :{self.username}")
        if request_tags:
            self.send("CAP REQ :twitch.tv/commands twitch.tv/tags")

    def join(self, channel_name: str):
        self.send(f"JOIN #{channel_name}")

    def poll(self, timeout_seconds: float = 1.0) -> Iterator[PrivMsg]:
        self.sock.settimeout(timeout_seconds)
        try:
            rcvd = self.sock.recv(4096)
        except TimeoutError:
            return

        self.buffer += rcvd

        lines = self.buffer.split(b'\r\n')
        self.buffer = lines[-1]

        for line in lines[:-1]:
            line = line.decode("utf-8").strip()

            if not line:
                continue

            msg = Message.parse(line)

            if msg.command == "PING":
                self.send(line.replace("PING", "PONG"))
            if isinstance(msg, PrivMsg):
                yield msg

    def say(self, target: str, msg: str):
        self.send(f"PRIVMSG {target} :{msg}")

    def send(self, msg: str):
        self.sock.send(f"{msg}\r\n".encode())

    def disconnect(self):
        self.send("QUIT")
        self.sock.close()


if __name__ == "__main__":
    bot = Bot()
    bot.connect()
    channel = input("channel to connect to? ")
    bot.join(channel)
    while True:
        for msg in bot.poll():
            print(f"<{msg.sender}> {msg.msg!r}")
