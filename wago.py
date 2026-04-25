"""Fix the wagokanji template.

Method:
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

import re

from main import (
    Header,
    extract_prelude,
    try_repl_with_callback,
)


def try_repl_wago(s: str, header: Header) -> str | None:
    return try_repl_with_callback(s, header, try_repl_wago_section)


def try_repl_wago_section(section: list[str], header: Header) -> list[str] | None:
    prelude = extract_prelude(section, header)  # type: ignore
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

    reading = extract_reading_from_reference(section[prelude.idx])
    if not reading:
        return None
    print(f"Found {reading=}")

    return [
        "==={{wago}}===",
        f"{{{{ja-wagokanji|{reading}}}}}",
        f"#{{{{wagokanji of|{reading}}}}}",
        *section[prelude.idx + 1 :],
    ]


def skip_empty_lines(idx: int, lines: list[str]) -> int:
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    return idx


def extract_reading_from_reference(s: str) -> str | None:
    # Match patterns like '''[[わかれ]]''' or 「'''[[かんがえ]]'''」
    match = re.search(r"[「']?\s*'''?\[\[(.+?)\]\]'''?\s*[」']?\s*(?:を)?参照", s)
    return match.group(1) if match else None


def repl_wago(s: str) -> str:
    for header in ("和語の漢字表記", "noun"):
        s = try_repl_wago(s, header) or s
    return s


def main() -> None:
    import test_wago

    test_wago.test_repl_wago_multiple()


if __name__ == "__main__":
    main()
