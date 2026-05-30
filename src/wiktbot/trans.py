import re

from wiktbot.reading import (
    Pos,
    try_repl_with_callback,
)

RAW_LANG_MAP = {
    "英語": "en",
}
RAW_LANG_PATTERN = "|".join(re.escape(k) for k in RAW_LANG_MAP)


def try_repl_trans(s: str, pos: Pos) -> str | None:
    return try_repl_with_callback(s, pos, try_repl_trans_section)


def try_repl_trans_section(section: list[str], _: Pos) -> list[str] | None:
    return [repl_line(line) for line in section]


def repl_line(line: str) -> str:
    m = re.match(r"\*\s?(?:\[\[)?\{\{(\w{2})\}\}(?:\]\])?[:：] ?(.+)", line)
    if not m:
        # Fallback to raw lang: *英語: [[homeomorphism]]
        m = re.match(rf"\*\s?({RAW_LANG_PATTERN})[:：] ?(.+)", line)
        if not m:
            return line
        lang = RAW_LANG_MAP[m.group(1)]
    else:
        lang = m.group(1)
    words = try_extract_words(m.group(2))
    if not words:
        return line
    translations = ", ".join(f"{{{{t|{lang}|{w}}}}}" for w in words)
    return f"*{{{{T|{lang}}}}}: {translations}"


def try_extract_words(s: str) -> list[str]:
    if bold_words := re.findall(r"\[\[(.+?)\]\]", s):
        return bold_words
    return []


def repl_trans(s: str) -> str:
    for pos in ("trans",):
        s = try_repl_trans(s, pos) or s
    return s
