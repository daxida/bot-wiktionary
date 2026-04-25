import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, get_args

# Duplication is smelly, but there are no runtime alternatives.
# The distinction is only important because of the extra {{ }} when parsing the header.
Pos = Literal["noun", "noun-suru", "adverb", "name", "trans"]
Header = Literal["和語の漢字表記", "noun", "noun-suru", "adverb", "name", "trans"]
POS_CHOICES = get_args(Pos)


@dataclass
class Prelude:
    idx: int
    new_header: Header | None
    categories: list[str]
    wikipedia: list[str]


def template_name(header: Header) -> str:
    match header:
        case "adverb":
            return "adv"
        case _:
            return header


def try_repl_with_callback(
    s: str,
    header: Header,
    callback: Callable[[list[str], Header], list[str] | None],
) -> str | None:
    lines = s.splitlines()

    idxs = extract_headers(lines, header)
    if not idxs:
        return None

    sections = list(zip(idxs, idxs[1:] + [len(lines)]))
    result_lines = lines[: idxs[0]]
    changed = False

    for fr, to in sections:
        section = lines[fr:to]
        replaced = callback(section, header)
        if replaced is None:
            result_lines.extend(section)
        else:
            # print(f"Found replacement at section {fr}-{to}")
            result_lines.extend(replaced)
            changed = True
    if not changed:
        return None

    return "\n".join(result_lines)


def try_repl(s: str, header: Pos) -> str | None:
    return try_repl_with_callback(s, header, try_repl_section)


def try_repl_section(section: list[str], header: Header) -> list[str] | None:
    prelude = extract_prelude(section, header)
    # print(f"Found {prelude=} {section=}")
    if prelude.idx == 1:
        return None

    if prelude.new_header is not None:
        header = prelude.new_header

    reading = None
    for label, extract_fn in (
        ("bold", extract_reading_bold_kanji),
        ("jachar", extract_reading_jachar),
    ):
        if reading := extract_fn(section[prelude.idx]):
            # print(f"Found {label} {reading=}")
            break
    if not reading:
        return None

    readings: list[str] = [reading]

    if not is_kana_only(reading):
        # print(f"[WARN] {reading=} is not kana-only. Trying multiple readings...")
        if many_readings := try_split_reading(reading):
            readings = many_readings
        else:
            return None

    to_add = f"{{{{ja-{template_name(header)}|{'|'.join(readings)}}}}}"

    return [
        *section[:1],
        *prelude.wikipedia,
        to_add,
        *prelude.categories,
        *section[prelude.idx + 1 :],
    ]


def extract_headers(lines: list[str], header: Header) -> list[int]:
    return [i for i, line in enumerate(lines) if try_parse_header(line, header)]


SURU_VERB_CATEGORIES = [
    "[[Category:{{ja}}_{{noun}}_サ変動詞]]",
    "[[Category:{{ja}} {{noun}}_サ変動詞]]",
]


def extract_prelude(lines: list[str], header: Header) -> Prelude:
    """Consume the prelude, that is, the lines between the header header, and
    the line that contains the reading.

    This includes categories, wikipedia links etc.

    Categories should go after the {{ja-X}} template; wikipedia links, before.
    """
    idx = 1
    categories: list[str] = []
    wikipedia: list[str] = []
    new_header: Pos | None = None

    while idx < len(lines):
        line = lines[idx]
        if not try_parse_category(line):
            if not try_parse_wikipedia_link(line):
                break
            else:
                wikipedia.append(line)
                idx += 1
                continue
        if header == "noun" and line in SURU_VERB_CATEGORIES:
            new_header = "noun-suru"
        if not is_removable_category(header, line):
            categories.append(line)
        idx += 1

    return Prelude(
        idx=idx,
        new_header=new_header,
        categories=categories,
        wikipedia=wikipedia,
    )


def is_kana_only(s: str) -> bool:
    if not s:
        return False
    allowed_extras = "[]-"
    return all(
        "\u3040" <= c <= "\u309f"  # hiragana
        or "\u30a0" <= c <= "\u30ff"  # katakana
        or c in allowed_extras
        for c in s
    )


def extract_reading_jachar(s: str) -> str | None:
    # {{jachar|X|Y}} supports args
    # {{jachars}} with s, is supposed to be written without...
    # ...but one can see the WRONG version too: {{jachars|アフリカ}}
    # so let's just reason as if {{jachars}} could also take args
    match = re.search(r"{{jachars?(?:\|[^}]*)?}}\s*[（(](.+?)[）)]", s)
    return match.group(1) if match else None


def extract_reading_bold_kanji(s: str) -> str | None:
    """Extract: '''text'''（reading）"""
    match = re.search(r"(?:'''(.+?)'''|(.+?))[（【](.+?)[）】]", s)
    return clean(match.group(3)) if match else None


def clean(s: str) -> str:
    return s.strip("'")


def try_parse_header(s: str, header: Header) -> bool:
    if header in POS_CHOICES:
        # There can be readings after the pos: ==={{noun}}：ぎぶつ===
        # There can be readings spaces between: === {{noun}} ===
        return (
            re.search(rf"===\s*\{{\{{{re.escape(header)}\}}\}}[^={{}}]*===", s)
            is not None
        )
    else:
        return re.search(rf"==={re.escape(header)}===", s) is not None


def try_parse_wikipedia_link(s: str) -> bool:
    return re.search(r"\{\{wikipedia\|[^}]*\}\}", s) is not None


def try_parse_category(s: str, cat: str = "") -> bool:
    inner = cat if cat else r"[^\]]+"
    return re.search(rf"\[\[(?:[Cc]ategory|カテゴリ):{inner}\]\]", s) is not None


def is_removable_category(pos: Header, cat: str) -> bool:
    return (
        re.search(rf"\[\[(?:[Cc]ategory|カテゴリ):{{{{ja}}}}[ _]{{{{{pos}}}}}", cat)
        is not None
    )


SEPARATORS = ",、"


# If there is a separator, and it's in the middle, assume multiple readings!
def try_split_reading(s: str) -> list[str]:
    for sep in SEPARATORS:
        if sep in s and not s.startswith(sep) and not s.endswith(sep):
            return [reading.strip() for reading in s.split(sep)]
    return []


def repl_reading(s: str) -> str:
    for pos in ("noun", "adverb", "name"):
        s = try_repl(s, pos) or s
    return s
