import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, get_args

Pos = Literal[
    "wago",
    "noun",
    "noun-suru",
    "adverb",
    "name",
    "trans",
    "adj",
    "verb",
    "idiom",
    "prefix",
    "suffix",
    # This header is level 4 (====), yet this works?
    "trans",
]
POS_CHOICES = get_args(Pos)


@dataclass
class Prelude:
    idx: int
    new_pos: Pos | None
    categories: list[str]
    wikipedia: list[str]


def template_name(pos: Pos) -> str:
    match pos:
        case "adverb":
            return "adv"
        case _:
            return pos


# https://ja.wiktionary.org/wiki/Wiktionary:テンプレートの一覧#品詞表記
def header(pos: Pos) -> str:
    match pos:
        case "wago":
            return "和語の漢字表記"
        case "noun":
            return "名詞"
        case "adverb":
            return "副詞"
        case "name":
            return "固有名詞"
        case "adj":
            return "形容詞"
        case "verb":
            return "動詞"
        case "idiom":
            return "成句"
        case "prefix":
            return "接頭辞"
        case "suffix":
            return "接尾辞"
        case "trans":
            return "翻訳"
        # This can't be found as a header
        case "noun-suru":
            return "noun-suru"


def try_repl_with_callback(
    s: str,
    pos: Pos,
    callback: Callable[[list[str], Pos], list[str] | None],
) -> str | None:
    lines = s.splitlines()

    idxs = extract_and_fix_headers(lines, pos)
    if not idxs:
        return None

    sections = list(zip(idxs, idxs[1:] + [len(lines)]))
    result_lines = lines[: idxs[0]]
    changed = False

    for fr, to in sections:
        section = lines[fr:to]
        replaced = callback(section, pos)
        if replaced is None:
            result_lines.extend(section)
        else:
            # print(f"Found replacement at section {fr}-{to}")
            result_lines.extend(replaced)
            changed = True
    if not changed:
        return None

    return "\n".join(result_lines)


def try_repl(s: str, pos: Pos) -> str | None:
    return try_repl_with_callback(s, pos, try_repl_section)


def try_repl_section(section: list[str], pos: Pos) -> list[str] | None:
    prelude = extract_prelude(section, pos)
    # print(f"Found:\n* {prelude=}\n* {section=}\n* {pos=}")
    if prelude.idx == 1:
        return None

    if prelude.new_pos is not None:
        pos = prelude.new_pos

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

    result = parse_readings(reading)
    if result is None:
        return None
    readings, extra_readings = result

    extra_readings_str = "" if not extra_readings else f" ({', '.join(extra_readings)})"
    to_add = f"{{{{ja-{template_name(pos)}|{'|'.join(readings)}}}}}{extra_readings_str}"

    return [
        *section[:1],
        *prelude.wikipedia,
        to_add,
        *prelude.categories,
        *section[prelude.idx + 1 :],
    ]


def extract_and_fix_headers(lines: list[str], pos: Pos) -> list[int]:
    """Return a list of indexes where there are headers.

    Raw Japanese headers (e.g. ===名詞===) are rewritten in-place to their
    template form (e.g. ==={{noun}}===).
    """
    idxs = []
    for i, line in enumerate(lines):
        # Template form
        # There can be readings after the pos: ==={{noun}}：ぎぶつ===
        # There can be readings spaces between: === {{noun}} ===
        if re.search(rf"===\s*\{{\{{{re.escape(pos)}\}}\}}[^={{}}]*===", line):
            idxs.append(i)
        # Raw Japanese header
        elif re.search(rf"==={re.escape(header(pos))}===", line):
            idxs.append(i)
            lines[i] = re.sub(
                rf"==={re.escape(header(pos))}===", f"==={{{{{pos}}}}}===", line
            )
    return idxs


SURU_VERB_CATEGORIES = [
    "[[Category:{{ja}}_{{noun}}_サ変動詞]]",
    "[[Category:{{ja}} {{noun}}_サ変動詞]]",
]


def extract_prelude(lines: list[str], pos: Pos) -> Prelude:
    """Consume the prelude, that is, the lines between the header, and the line
    that contains the reading.

    This includes categories, wikipedia links etc.

    Categories should go after the {{ja-X}} template; wikipedia links, before.
    """
    idx = 1
    categories: list[str] = []
    wikipedia: list[str] = []
    new_pos: Pos | None = None

    while idx < len(lines):
        line = lines[idx]
        if not line:
            idx += 1
            continue
        if not try_parse_category(line):
            if not try_parse_wikipedia_link(line):
                break
            else:
                wikipedia.append(line)
                idx += 1
                continue
        if pos == "noun" and line in SURU_VERB_CATEGORIES:
            new_pos = "noun-suru"
        if not is_category_removable(pos, line):
            categories.append(line)
        idx += 1

    # Backtrack if we found a gloss
    if idx < len(lines) and lines[idx].startswith("#"):
        idx -= 1

    return Prelude(
        idx=idx,
        new_pos=new_pos,
        categories=categories,
        wikipedia=wikipedia,
    )


def parse_readings(reading: str) -> tuple[list[str], list[str]] | None:
    """Returns (readings, extra_readings) or None if parsing fails."""
    if is_kana_only(reading):
        return [reading], []

    # print(f"[WARN] {reading=} is not kana-only. Trying multiple readings...")
    many_readings = try_split_reading(reading)
    if not many_readings:
        # print("[WARN] 001 Failed multiple readings. Returning.")
        return None

    if all(is_kana_only(r) for r in many_readings):
        return many_readings, []

    # print(f"[WARN] Found {many_readings=} but they were not kana.")
    for prefix in ("稀:", "やや古:"):
        if all(is_kana_only(r) or r.startswith(prefix) for r in many_readings):
            readings = [r for r in many_readings if not r.startswith(prefix)]
            extra_readings = [r for r in many_readings if r.startswith(prefix)]
            return readings, extra_readings

    # print("[WARN] 002 Failed multiple readings. Returning.")
    return None


def is_kana_only(s: str) -> bool:
    if not s:
        return False
    allowed_extras = "[]-"
    # Don't allow hyphens at edges due to prefixes/suffixes
    if s[0] == "-" or s[-1] == "-":
        return False
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
    match = re.search(r"(?:'''(.+?)'''|(.+?))[（(【](.+?)[）)】]", s)
    return clean(match.group(3)) if match else None


def clean(s: str) -> str:
    return s.strip("'")


def try_parse_wikipedia_link(s: str) -> bool:
    return re.search(r"\{\{wikipedia\|[^}]*\}\}", s) is not None


def try_parse_category(s: str, cat: str = "") -> bool:
    inner = cat if cat else r"[^\]]+"
    return re.search(rf"\[\[(?:[Cc]ategory|カテゴリ):{inner}\]\]", s) is not None


def is_category_removable(pos: Pos, cat: str) -> bool:
    return (
        re.search(
            rf"\[\[(?:[Cc]ategory|カテゴリ):(?:日本語|{{{{ja}}}})[ _]{{{{{pos}}}}}", cat
        )
        is not None
    )


def is_category_ja(line: str) -> bool:
    # * [[カテゴリ:日本語]]
    # * [[カテゴリ:{{ja}}]]
    # * [[Category:{{ja}}]]
    # * [[Category:日本語]]
    # * [[Category:{{ja}}|れんしよう れんじょう]]
    return (
        re.search(
            r"\[\[(?:[Cc]ategory|カテゴリ):(?:日本語|\{\{ja\}\})(?:\|[^\]]+)?\]\]",
            line,
        )
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
    found = False
    for pos in ("noun", "adverb", "name", "adj", "verb", "idiom", "prefix", "suffix"):
        if replacement := try_repl(s, pos):
            found = True
            s = replacement

    # If we found a replacement, we can remove the category: [[カテゴリ:日本語]]
    # anywhere on the wikitext (according to @Naggy Nagumo)
    if found:
        s = "\n".join(
            line for line in s.splitlines() if not is_category_ja(line.strip())
        )

    return s
