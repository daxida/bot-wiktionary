import re
from dataclasses import dataclass
from typing import Literal, get_args

Pos = Literal["noun", "noun-suru", "adverb", "name"]
Header = Literal["和語の漢字表記"]
POS_CHOICES = get_args(Pos)


@dataclass
class Prelude:
    idx: int
    new_pos: Pos | None
    categories: list[str]
    wikipedia: list[str]


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

    # try parse (one or more) pos sections
    idxs_pos = extract_poses(lines, pos)
    if not idxs_pos:
        return None
    idxs_pos.append(len(lines))
    sections = [(idxs_pos[i], idxs_pos[i + 1]) for i in range(len(idxs_pos) - 1)]

    def try_repl_jachar_section(pos: Pos, section: list[str]) -> list[str] | None:
        prelude = extract_prelude(section, 0, pos)
        if prelude.idx == 1:
            return None
        if prelude.new_pos is not None:
            pos = prelude.new_pos
        print(f"[jachar] Found {prelude=}")
        print(f"[jachar] Line after prelude {lines[prelude.idx]}")

        reading = extract_reading_jachar(s)
        if not reading:
            return None
        print(f"[jachar] Found {reading=}")

        if not is_kana_only(reading):
            print(f"[WARN] {reading=} is not kana-only")
            return None

        to_add = f"{{{{ja-{pos}|{reading}}}}}"

        new_lines = section[:1]  # up until (included) pos
        new_lines.extend(prelude.wikipedia)
        new_lines.append(to_add)
        new_lines.extend(prelude.categories)
        new_lines.extend(section[prelude.idx + 1 :])  # after jachar

        return new_lines

    first_start = sections[0][0]
    result_lines: list[str] = lines[:first_start]
    changed = False
    for fr, to in sections:
        section = lines[fr:to]
        replaced = try_repl_jachar_section(pos, section)
        if replaced is None:
            result_lines.extend(section)
        else:
            print(f"[jachar] Found replacement at section {fr}-{to}")
            result_lines.extend(replaced)
            changed = True
    if not changed:
        return None

    return "\n".join(result_lines)


def try_repl_bold(s: str, pos: Pos) -> str | None:
    lines = s.splitlines()

    # try parse (one or more) pos sections
    idxs_pos = extract_poses(lines, pos)
    if not idxs_pos:
        return None
    idxs_pos.append(len(lines))
    sections = [(idxs_pos[i], idxs_pos[i + 1]) for i in range(len(idxs_pos) - 1)]

    def try_repl_bold_section(pos: Pos, section: list[str]) -> list[str] | None:
        prelude = extract_prelude(section, 0, pos)
        print(f"[bold] Found {prelude=} {section=}")
        if prelude.idx == 1:
            return None
        if prelude.new_pos is not None:
            pos = prelude.new_pos
        print(f"[bold] Found {prelude=}")

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

        new_lines = section[:1]  # up until (included) pos
        new_lines.extend(prelude.wikipedia)
        new_lines.append(to_add)
        new_lines.extend(prelude.categories)
        new_lines.extend(section[prelude.idx + 1 :])  # after jachar

        return new_lines

    first_start = sections[0][0]
    result_lines: list[str] = lines[:first_start]
    changed = False
    for fr, to in sections:
        section = lines[fr:to]
        # print(f"[bold] Trying replacement at section {fr}-{to}...")
        replaced = try_repl_bold_section(pos, section)
        if replaced is None:
            result_lines.extend(section)
        else:
            print(f"[bold] Found replacement at section {fr}-{to}")
            result_lines.extend(replaced)
            changed = True
    if not changed:
        return None

    return "\n".join(result_lines)


def extract_poses(lines: list[str], pos: Pos) -> list[int]:
    return [i for i, line in enumerate(lines) if try_parse_pos(line, pos)]


def extract_header(lines: list[str], header: Header) -> list[int]:
    return [i for i, line in enumerate(lines) if try_parse_header(line, header)]


def extract_prelude(lines: list[str], idx_pos: int, pos: Pos) -> Prelude:
    """Consume the prelude, that is, the lines between the pos header, and
    the line that contains the reading.

    This includes categories, wikipedia links etc.

    Categories should go after the {{ja-X}} template; wikipedia links, before.
    """
    idx = idx_pos
    idx += 1
    categories: list[str] = []
    wikipedia: list[str] = []
    new_pos: Pos | None = None

    while idx < len(lines):
        line = lines[idx]
        if not try_parse_category(line):
            if not try_parse_wikipedia_link(line):
                break
            else:
                wikipedia.append(line)
                idx += 1
                continue
        if pos == "noun" and line in SURU_VERB_CATEGORIES:
            new_pos = "noun-suru"
        if not is_removable_category(pos, line):
            categories.append(line)
        idx += 1

    return Prelude(
        idx=idx,
        new_pos=new_pos,
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


def try_parse_pos(s: str, pos: Pos) -> bool:
    # There can be readings after the pos: ==={{noun}}：ぎぶつ===
    # There can be readings spaces between: === {{noun}} ===
    return re.search(rf"===\s*\{{\{{{re.escape(pos)}\}}\}}[^={{}}]*===", s) is not None


def try_parse_header(s: str, header: Header) -> bool:
    return re.search(rf"==={re.escape(header)}===", s) is not None


def try_parse_wikipedia_link(s: str) -> bool:
    return re.search(r"\{\{wikipedia\|[^}]*\}\}", s) is not None


def try_parse_category(s: str, cat: str = "") -> bool:
    inner = cat if cat else r"[^\]]+"
    return re.search(rf"\[\[(?:[Cc]ategory|カテゴリ):{inner}\]\]", s) is not None


def is_removable_category(pos: Pos, cat: str) -> bool:
    return (
        re.search(rf"\[\[(?:[Cc]ategory|カテゴリ):{{{{ja}}}}[ _]{{{{{pos}}}}}", cat)
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
        s = repl
    if repl := try_repl_bold(s, pos):
        print(f"[!] Success: bold for {pos=}")
        s = repl

    return s


def repl_ja_template(s: str) -> str:
    for pos in ("noun", "adverb", "name"):
        s = repl_ja_template_with_pos(s, pos)
    return s


def main() -> None:
    import test_main

    test_main.test_repl_ja_bold_base()
    # test_main.test_repl_ja_bold_multiple()


if __name__ == "__main__":
    main()
