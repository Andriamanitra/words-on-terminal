from wot import truncate_username


def test_truncate():
    assert truncate_username("username") == "username"
    assert truncate_username("username", max_length=3) == "u6e"
    assert truncate_username("abcdefghi_abcdefghi_", max_length=12) == "abcdefghi_9_"
    assert truncate_username("abcdefghi_abcdefghi_abcde", max_length=12) == "abcdefghi15e"


def test_nick(nick="VeryVeryLongUserNickName"):
    for m in range(1, len(nick) + 1):
        truncated = truncate_username(nick, max_length=m)
        assert truncated[0] == nick[0], f"truncate_username({nick!r}, max_length={m}) should start with {nick[0]!r}"
        assert len(truncated) == m


if __name__ == "__main__":
    nick = "VeryVeryLongUserNickName"
    for m in range(1, len(nick) + 1):
        truncated = truncate_username(nick, max_length=m)
        print(f"{m:3d}  {nick!r} -> {truncated!r}")
