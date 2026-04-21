import re

from main import (
    POS_CHOICES,
    Header,
    extract_header,
    extract_poses,
    extract_prelude,
    Pos,
)


def try_repl_wago(s: str, pos: Pos | Header) -> str | None:
    """Method:
    1. Scan for:
        ===和語の漢字表記===
        [[Category:{{ja}} 和語の漢字表記]]
    2. Ignore next line (may contain reading!)
       ^ we should also try extracting reading there
    3. Try extracting reading from the next line.

    ===和語の漢字表記===
    [[Category:{{ja}} 和語の漢字表記]]
    '''[[考]] え'''
    #「'''[[かんがえ]]'''」参照。
    """
    lines = s.splitlines()

    # try parse (one or more) pos sections
    if pos in POS_CHOICES:
        print(f"Extracting {pos=}")
        idxs_pos = extract_poses(lines, pos)  # type: ignore
    else:
        print(f"Extracting header='{pos}'")
        idxs_pos = extract_header(lines, pos)  # type: ignore
    if not idxs_pos:
        print(f"No header found for {pos=}")
        return None
    idxs_pos.append(len(lines))
    sections = [(idxs_pos[i], idxs_pos[i + 1]) for i in range(len(idxs_pos) - 1)]

    for idx in idxs_pos[:-1]:
        print(f"Found {pos=} at line {idx}: {lines[idx]}")

    def try_repl_wago_section(
        pos: Pos | Header, section: list[str]
    ) -> list[str] | None:
        prelude = extract_prelude(section, 0, pos)  # type: ignore
        if prelude.idx == 1:
            # This is ok but remember that we skip one line!
            print("Didn't find prelude")
        else:
            print(f"Found {prelude=}")
        print(f"Line after prelude {section[prelude.idx]}")

        # Skip line (maybe we can narrow this to be more precise)
        # ex. of lines that we skip
        # - '''[[心]] [[のこり|残り]]'''（こころのこり）
        # - '''{{l|ja|想}}い'''
        # - {{lang|ja|'''[[奨]]める'''}}（すすめる）
        prelude.idx += 1
        prelude.idx = skip_empty_lines(prelude.idx, section)

        # Extract reading
        print(f"Extracting reading at {section[prelude.idx]}")
        reading = extract_reading_from_reference(section[prelude.idx])
        if not reading:
            return None
        print(f"Found {reading=}")

        to_add = [
            "==={{wago}}===",
            f"{{{{ja-wagokanji|{reading}}}}}",
            f"#{{{{wagokanji of|{reading}}}}}",
        ]

        new_lines = []  # up until (excluded) pos
        new_lines.extend(to_add)
        new_lines.extend(section[prelude.idx + 1 :])

        return new_lines

    first_start = sections[0][0]
    result_lines: list[str] = lines[:first_start]
    changed = False
    for fr, to in sections:
        section = lines[fr:to]
        replaced = try_repl_wago_section(pos, section)
        if replaced is None:
            result_lines.extend(section)
        else:
            print(f"[wago] Found replacement at section {fr}-{to}")
            result_lines.extend(replaced)
            changed = True
    if not changed:
        return None

    return "\n".join(result_lines)


def skip_empty_lines(idx: int, lines: list[str]) -> int:
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    return idx


def extract_reading_from_reference(s: str) -> str | None:
    # Match patterns like '''[[わかれ]]''' or 「'''[[かんがえ]]'''」
    match = re.search(r"[「']?\s*'''?\[\[(.+?)\]\]'''?\s*[」']?\s*(?:を)?参照", s)
    return match.group(1) if match else None


def repl_wago_with_pos(s: str, pos: Pos | Header) -> str:
    if repl := try_repl_wago(s, pos):
        return repl

    return s


def repl_wago(s: str) -> str:
    for pos in ("和語の漢字表記", "noun"):
        s = repl_wago_with_pos(s, pos)
    return s


def main() -> None:
    import test_wago

    test_wago.test_repl_wago_multiple()


if __name__ == "__main__":
    main()
