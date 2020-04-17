import re


def alnum_parser(s, lower):
    # sentence -> sentence
    # remove anything including whitespace but 0-9 and a-z, A-Z
    # have uniform whitespace b/w words
    filtered = [ch if ch.isalnum() else " " for ch in s]
    s = "".join(filtered)
    s = " ".join(s.split())
    if lower:
        s = s.lower()
    return s


def whitespaced_split(s):
    # sentence -> list of words
    # preserve white space in splitting sentence
    return re.split(r'(\s+)', s)
