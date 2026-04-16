import re

from main import (
    try_parse_category,
    try_parse_header,
)


def try_repl_wago(s: str) -> str | None:
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

    # try_parse pos
    pos = "和語の漢字表記"
    idx_pos = -1
    for i, line in enumerate(lines):
        if try_parse_header(line, pos):
            idx_pos = i
            break

    if idx_pos == -1:
        return None
    print(f"Found {pos=}")

    # consume categories
    idx_cat = idx_pos
    idx_cat += 1
    while idx_cat < len(lines) and try_parse_category(lines[idx_cat]):
        idx_cat += 1
    if idx_cat == idx_pos + 1:
        return None
    print("Found some categories")

    # Skip line
    idx_cat += 1

    # Skip potentially empty lines (TODO: extract this into a function)
    while idx_cat < len(lines) and not lines[idx_cat].strip():
        idx_cat += 1

    # Extract reading
    reading = extract_reading_from_reference(lines[idx_cat])
    if not reading:
        return None
    print(f"Found {reading=}")

    to_add = f"""==={{{{wago}}}}===
{{{{ja-wagokanji|{reading}}}}}
#{{{{wagokanji of|{reading}}}}}"""

    new_lines = lines[:idx_pos]  # up until (excluded) pos
    new_lines.append(to_add)
    new_lines.extend(lines[idx_cat + 1 :])

    return "\n".join(new_lines)


def extract_reading_from_reference(s: str) -> str | None:
    # Match patterns like '''[[わかれ]]''' or 「'''[[かんがえ]]'''」
    match = re.search(r"[「']?\s*'''?\[\[(.+?)\]\]'''?\s*[」']?\s*(?:を)?参照", s)
    return match.group(1) if match else None


def repl_wago(s: str) -> str:
    if repl := try_repl_wago(s):
        return repl

    return s


def main() -> None:
    import test_wago

    test_wago.test_repl_wago4()


if __name__ == "__main__":
    main()
