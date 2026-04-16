import re
from typing import Literal

Pos = Literal["noun", "noun-suru", "adverb"]


SURU_VERB_CATEGORIES = [
    "[[Category:{{ja}}_{{noun}}_サ変動詞]]",
    "[[Category:{{ja}} {{noun}}_サ変動詞]]",
]


def template_name(pos: Pos) -> str:
    match pos:
        case "adverb":
            return "adv"
        case _:
            return pos


# jachar or jachars actually
# TODO: support multiple readings
def try_repl_jachar(s: str, pos: Pos) -> str | None:
    lines = s.splitlines()

    # try_parse pos
    idx_pos = -1
    for i, line in enumerate(lines):
        if try_parse_pos(line, pos):
            idx_pos = i
            break

    if idx_pos == -1:
        return None
    print(f"[jachar] Found {pos=}")

    # extract categories
    idx_cat = idx_pos
    idx_cat += 1
    categories: list[str] = []
    new_pos: str | None = None
    while idx_cat < len(lines) and try_parse_category(lines[idx_cat]):
        cat = lines[idx_cat]
        if pos == "noun" and cat in SURU_VERB_CATEGORIES:
            new_pos = "noun-suru"
        if not is_removable_category(pos, cat):
            categories.append(cat)
        idx_cat += 1
    if idx_cat == idx_pos + 1:
        return None
    if new_pos is not None:
        pos = new_pos
    print("[bold] Found some categories")

    reading = extract_reading_jachar(s)
    if not reading:
        return None
    print(f"[jachar] Found {reading=}")

    if not is_kana_only(reading):
        print(f"[WARN] {reading=} is not kana-only")
        return None

    to_add = f"{{{{ja-{pos}|{reading}}}}}"

    new_lines = lines[: idx_pos + 1]  # up unti pos included
    new_lines.append(to_add)
    new_lines.extend(categories)
    new_lines.extend(lines[idx_cat + 1 :])  # after jachar

    return "\n".join(new_lines)


def try_repl_bold(s: str, pos: Pos) -> str | None:
    # Scuffed parser
    lines = s.splitlines()

    # try_parse pos
    idx_pos = -1
    for i, line in enumerate(lines):
        if try_parse_pos(line, pos):
            idx_pos = i
            break

    if idx_pos == -1:
        return None
    print(f"[bold] Found {pos=}")

    # extract categories
    idx_cat = idx_pos
    idx_cat += 1
    categories: list[str] = []
    new_pos: str | None = None
    while idx_cat < len(lines) and try_parse_category(lines[idx_cat]):
        cat = lines[idx_cat]
        if pos == "noun" and cat in SURU_VERB_CATEGORIES:
            new_pos = "noun-suru"
        if not is_removable_category(pos, cat):
            categories.append(cat)
        idx_cat += 1
    if idx_cat == idx_pos + 1:
        return None
    if new_pos is not None:
        pos = new_pos
    print("[bold] Found some categories")

    reading = extract_reading_bold_kanji(s)
    if not reading:
        return None
    print(f"[bold] Found {reading=}")

    readings: list[str] = [reading]

    if not is_kana_only(reading):
        print(f"[WARN] {reading=} is not kana-only")
        if many_readings := try_split_reading(reading):
            readings = many_readings
        else:
            return None

    final_reading = "|".join(readings)
    pos_template_name = template_name(pos)
    to_add = f"{{{{ja-{pos_template_name}|{final_reading}}}}}"

    new_lines = lines[: idx_pos + 1]  # up until (included) pos
    new_lines.append(to_add)
    new_lines.extend(categories)
    new_lines.extend(lines[idx_cat + 1 :])  # after jachar

    return "\n".join(new_lines)


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
    # {{jachars}} with s, can be written without args
    match = re.search(r"{{(?:jachar\|[^}]+|jachars)}}（(.+?)）", s)
    return match.group(1) if match else None


def extract_pos(s: str) -> str | None:
    """Extract part of speech from ==={{pos}}=== header."""
    match = re.search(r"===\{\{(.+?)\}\}===", s)
    return match.group(1) if match else None


def extract_reading_bold_kanji(s: str) -> str | None:
    """Extract: '''text'''（reading）"""
    match = re.search(r"(?:'''(.+?)'''|(.+?))[（【](.+?)[）】]", s)
    return clean(match.group(3)) if match else None


def clean(s: str) -> str:
    return s.strip("'")


def try_parse_pos(s: str, pos: str) -> bool:
    return re.search(rf"===\{{\{{{re.escape(pos)}\}}\}}===", s) is not None


def try_parse_header(s: str, header: str) -> bool:
    return re.search(rf"==={re.escape(header)}===", s) is not None


def try_parse_category(s: str, cat: str = "") -> bool:
    inner = cat if cat else r"[^\]]+"
    return re.search(rf"\[\[(?:Category|カテゴリ):{inner}\]\]", s) is not None


def is_removable_category(pos: Pos, cat: str) -> bool:
    return (
        re.search(rf"\[\[(?:Category|カテゴリ):{{{{ja}}}}[ _]{{{{{pos}}}}}", cat)
        is not None
    )


SEPARATORS = ","


# If there is a separator, and it's in the middle, assume multiple readings!
def try_split_reading(s: str) -> list[str]:
    for sep in SEPARATORS:
        if sep in s and not s.startswith(sep) and not s.endswith(sep):
            return [reading.strip() for reading in s.split(sep)]
    return []


def repl_ja_template_with_pos(s: str, pos: Pos) -> str:
    if repl := try_repl_jachar(s, pos):
        print(f"[!] Success: jachar for {pos=}")
        return repl
    if repl := try_repl_bold(s, pos):
        print(f"[!] Success: bold for {pos=}")
        return repl

    return s


def repl_ja_template(s: str) -> str:
    for pos in ("noun", "adverb"):
        s = repl_ja_template_with_pos(s, pos)
    return s


def main() -> None:
    import test_main

    test_main.test_repl_ja_bold_with_inner_category()


if __name__ == "__main__":
    main()
