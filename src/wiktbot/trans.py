import re

from wiktbot.reading import (
    Header,
    try_repl_with_callback,
)


def try_repl_trans(s: str, header: Header) -> str | None:
    return try_repl_with_callback(s, header, try_repl_trans_section)


def try_repl_trans_section(section: list[str], header: Header) -> list[str] | None:
    def repl_line(line: str) -> str:
        m = re.match(r"\*\{\{(\w+)\}\}: (.+)", line)
        if not m:
            return line
        lang = m.group(1)
        words = re.findall(r"\[\[(.+?)\]\]", m.group(2))
        if not words:
            return line
        translations = ", ".join(f"{{{{t|{lang}|{w}}}}}" for w in words)
        return f"*{{{{T|{lang}}}}}: {translations}"

    return [repl_line(line) for line in section]


def repl_trans(s: str) -> str:
    for header in ("trans",):
        s = try_repl_trans(s, header) or s
    return s
