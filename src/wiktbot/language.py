"""Fix language headers.

=={{ja}}== becomes =={{L|ja}}==
"""

import re
from typing import Literal, get_args

Lang = Literal["ja", "zh", "ko", "vi"]


def header(lang: Lang) -> str:
    match lang:
        case "ja":
            return "日本語"
        case "zh":
            return "中国語"
        case "ko":
            return "朝鮮語"
        case "vi":
            return "ベトナム語"


# See reading.py::extract_and_fix_headers
def repl_language_line(line: str) -> str:
    for lang in get_args(Lang):
        # Already in correct template form =={{L|ja}}==
        if re.search(rf"==\s*\{{\{{L\|{re.escape(lang)}\}}\}}\s*==", line):
            break
        # Template form =={{ja}}== → =={{L|ja}}==
        if re.search(rf"==\s*\{{\{{{re.escape(lang)}\}}\}}\s*==", line):
            return re.sub(
                rf"==\s*\{{\{{{re.escape(lang)}\}}\}}\s*==",
                f"=={{{{L|{lang}}}}}==",
                line,
            )
        # Raw text header
        elif re.search(rf"==\s*{re.escape(header(lang))}\s*==", line):
            return re.sub(
                rf"==\s*{re.escape(header(lang))}\s*==",
                f"=={{{{L|{lang}}}}}==",
                line,
            )
    return line


def repl_language(s: str) -> str:
    return "\n".join(repl_language_line(line) for line in s.splitlines())
