import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, get_args

Pos = Literal[
    "wago",
    "noun",
    "noun-suru",
    "adjective",
    "adverb",
    "name",
    "pronoun",
    "trans",
    "adj",
    "verb",
    "idiom",
    "prefix",
    "suffix",
    "adnominal",
    "proverb",
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
        case "adjective":
            return "adj"
        case _:
            return pos


# https://ja.wiktionary.org/wiki/Wiktionary:テンプレートの一覧#品詞表記
def header(pos: Pos) -> str:
    match pos:
        case "wago":
            return "和語の漢字表記"
        case "noun":
            return "名詞"
        case "adjective":
            return "形容詞"
        case "adverb":
            return "副詞"
        case "name":
            return "固有名詞"
        case "pronoun":
            return "代名詞"
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
        case "adnominal":
            return "連体詞"
        case "proverb":
            return "ことわざ"
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
    if prelude.new_pos is not None:
        pos = prelude.new_pos

    line_with_reading = section[prelude.idx]
    # Also update pos if the line_with_reading has a correct template
    if pos == "noun" and "{{ja-noun-suru" in line_with_reading:
        pos = "noun-suru"

    reading = extract_reading(line_with_reading)
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
        else:
            header_re = re.compile(rf"===\s*{re.escape(header(pos))}\s*===")
            if header_re.search(line):
                idxs.append(i)
                lines[i] = header_re.sub(f"==={{{{{pos}}}}}===", line)
    return idxs


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
            # File links share behaviour with wikipedia links: they go at the top
            if not try_parse_wikipedia_link(line) and not try_parse_file_link(line):
                break
            else:
                wikipedia.append(line)
                idx += 1
                continue
        if pos == "noun" and is_category_suru(line):
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
    """Returns (readings, extra_readings) or None if parsing fails.

    To be precise, extra_readings can be readings or kanji variations etc.
    """

    # Kanji transliterations of kana-only pages (e.g. ころしや: [[殺]]し[[屋]]) can
    # appear wrapped in 【】 when editors don't use the proper template. Since we lack
    # page title context, we can't verify this, so we just pass it through.
    if reading.startswith("【") and reading.endswith("】"):
        clean_reading = reading[1:-1]
        if is_japanese(clean_reading):
            return [clean_reading], []
        many_readings = try_split_reading(clean_reading)
        if many_readings and all(is_japanese(r) for r in many_readings):
            return many_readings, []

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
    for prefix in ("稀:", "やや古:", "古:", "異表記:"):
        if all(is_kana_only(r) or r.startswith(prefix) for r in many_readings):
            readings = [r for r in many_readings if not r.startswith(prefix)]
            extra_readings = [r for r in many_readings if r.startswith(prefix)]
            return readings, extra_readings

    # print("[WARN] 002 Failed multiple readings. Returning.")
    return None


ALLOWED_READING_EXTRA_CHARS = "[]-"
"""Brackets are used for wikilinks, hyphens for mixed scripts transliterations."""


def _is_kana(c: str) -> bool:
    return (
        "\u3040" <= c <= "\u309f"  # hiragana
        # NOTE: we exclude ・ because it is treated as a separator
        or ("\u30a0" <= c <= "\u30ff" and c != "\u30fb")  # katakana (excluding ・)
    )


def is_kana_only(s: str) -> bool:
    if not s:
        return False
    # Don't allow hyphens at edges due to prefixes/suffixes
    if s[0] == "-" or s[-1] == "-":
        return False
    return all(_is_kana(c) or c in ALLOWED_READING_EXTRA_CHARS for c in s)


def is_japanese(s: str) -> bool:
    if not s:
        return False
    return all(
        _is_kana(c)
        or "\u4e00" <= c <= "\u9fff"  # CJK unified ideographs (kanji)
        or "\u3400" <= c <= "\u4dbf"  # CJK extension A
        or "\uf900" <= c <= "\ufaff"  # CJK compatibility ideographs
        or c in ALLOWED_READING_EXTRA_CHARS
        for c in s
    )


def is_japanese_or_separator(s: str) -> bool:
    return all(is_japanese(c) or c in SEPARATORS for c in s)


# Reading with Kanji (and possibly kana) of a kana-only headword
def is_kanji_reading(s: str) -> bool:
    # * 【咳き込む】
    # * 【[[噎]]ぶ、[[咽]]ぶ】
    return is_japanese_or_separator(s) and not is_kana_only(s)


def extract_reading(s: str) -> str | None:
    for _, extract_fn in (
        ("bold", extract_reading_bold),
        ("jachar", extract_reading_jachar),
        ("head", extract_reading_head),
        ("template", extract_reading_template),
    ):
        if reading := extract_fn(s):
            # print(f"Found {_} {reading=}")
            return reading
    return None


def extract_reading_bold(s: str) -> str | None:
    """Extract reading from: '''text'''（reading）

    It also extracts the common faulty version: text (reading)
    We exclude brackets to not match templates in that position.
    """
    match = re.search(r"(?:'''[^{}]+?'''|[^{}]+?)([（(【])(.+?)([）)】])", s)
    return postprocess_reading(match) if match else None


def extract_reading_jachar(s: str) -> str | None:
    """Extract reading from: {{jachar}}（reading） or {{jachars}}（reading）"""
    # {{jachar|X|Y}} supports args
    # {{jachars}} is supposed to be written without args, but faulty pages
    # may use {{jachars|アフリカ}}, so args are accepted for both forms.
    match = re.search(r"{{jachars?(?:\|[^}]*)?}}\s*([（(【])(.+?)([）)】])", s)
    return postprocess_reading(match) if match else None


def extract_reading_head(s: str) -> str | None:
    """Extract reading from: {{head|ja...}}（reading）

    Note that there can be nested {{templates}} in ...
    """
    match = re.search(r"\{\{head\|ja.*\}\}\s*([（(【])(.+?)([）)】])", s)
    return postprocess_reading(match) if match else None


JA_TEMPLATES = "|".join(
    f"ja-{template_name(pos)}" for pos in POS_CHOICES if pos != "trans"
)


def extract_reading_template(s: str) -> str | None:
    """Extract reading from: {{ja-noun}}（reading）, {{ja-adv}}（reading）, etc."""
    match = re.search(
        rf"\{{\{{(?:{JA_TEMPLATES})[^}}]*\}}\}}\s*([（(【])(.+?)([）)】])", s
    )
    return postprocess_reading(match) if match else None


def postprocess_reading(match: re.Match[str]) -> str:
    """Process a regex match containing a bracketed reading.

    Handles two cases:
    - （）or （） brackets: return the inner content as-is.
    - 【】 brackets
      - re-wrap with 【】 so that parse_readings can detect and handle kanji
        transcriptions of kana-only pages (e.g. 【殺し屋】).
      - However, if the inner content is kana-only or contains separators, it is
        a faulty page where 【】 was used instead of （）: return plain inner
        content so it is treated as a normal reading.
    """
    open_b, inner, close_b = match.group(1), clean(match.group(2)), match.group(3)
    if open_b == "【" and close_b == "】" and is_kanji_reading(inner):
        return f"【{inner}】"
    return inner


def clean(s: str) -> str:
    return s.strip("'")


def try_parse_wikipedia_link(s: str) -> bool:
    return re.search(r"\{\{wikipedia\|[^}]*\}\}", s) is not None


def try_parse_file_link(s: str) -> bool:
    return re.search(r"\[\[[Ff]ile:[^\]]+\]\]", s) is not None


def try_parse_category(s: str, cat: str = "") -> bool:
    inner = cat if cat else r"[^\]]+"
    return re.search(rf"\[\[(?:[Cc]ategory|カテゴリ):{inner}\]\]", s) is not None


def is_category_suru(line: str) -> bool:
    # * [[カテゴリ:{{ja}}_{{noun}}_サ変動詞|まんそく]]
    # * [[Category:{{ja}} {{noun}} サ変動詞|しんこう]]
    return (
        re.search(
            r"\[\[(?:[Cc]ategory|カテゴリ):(?:日本語|\{\{ja\}\})[ _](?:名詞|\{\{noun\}\})[ _]サ変動詞(?:\|[^\]]+)?\]\]",
            line,
        )
        is not None
    )


def is_category_removable(pos: Pos, cat: str) -> bool:
    # * [[Category:{{ja}}_{{noun}}]]
    # * [[Category:日本語_名詞]]
    return (
        re.search(
            rf"\[\[(?:[Cc]ategory|カテゴリ):(?:日本語|{{{{ja}}}})[ _](?:{{{{{pos}}}}}|{header(pos)})",
            cat,
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


SEPARATORS = ",、・　"


# If there is a separator, and it's in the middle, assume multiple readings!
def try_split_reading(s: str) -> list[str]:
    for sep in SEPARATORS:
        if sep in s and not s.startswith(sep) and not s.endswith(sep):
            return [reading.strip() for reading in s.split(sep)]
    return []


def repl_reading(s: str) -> str:
    found = False
    for pos in (
        "noun",
        "adjective",
        "adverb",
        "name",
        "pronoun",
        "adj",
        "verb",
        "idiom",
        "prefix",
        "suffix",
        "adnominal",
        # "proverb", # ja-proverb doesn't exist (but should)
    ):
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
