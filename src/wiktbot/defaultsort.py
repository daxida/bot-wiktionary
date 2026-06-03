"""Fix DEFAULTSORT template.

{{DEFAULTSORT:うつる}} becomes {{kana-DEFAULTSORT|うつる}}
"""

import re
from wiktbot.reading import is_kana_only

_SMALL_KANA = set("ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮヵヶ")
_VOICED_KANA = set(
    "がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽゔガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポヴ"
)


def _has_small_kana(s: str) -> bool:
    return any(c in _SMALL_KANA for c in s)


def _has_voiced(s: str) -> bool:
    return any(c in _VOICED_KANA for c in s)


# {{DEFAULTSORT:ほんふん ほんぶん}} > prefer ほんぶん
def _is_preferred(s: str) -> bool:
    return _has_voiced(s) or _has_small_kana(s)


def repl_defaultsort_line(line: str) -> str:
    if m := re.match(r"{{DEFAULTSORT:(.*)}}", line):
        readings = m.group(1).split(" ")
        match readings:
            # If there is exactly one reading: replace
            case [reading]:
                return f"{{{{kana-DEFAULTSORT|{reading}}}}}"
            case [r1, r2]:
                # Two word and one of them is {{PAGENAME}}, use the other
                if r1 == "{{PAGENAME}}":
                    return f"{{{{kana-DEFAULTSORT|{r2}}}}}"
                elif r2 == "{{PAGENAME}}":
                    return f"{{{{kana-DEFAULTSORT|{r1}}}}}"
                if not (is_kana_only(r1) and is_kana_only(r2)):
                    return line
                if _is_preferred(r2) and not _is_preferred(r1):
                    return f"{{{{kana-DEFAULTSORT|{r2}}}}}"
                else:
                    return f"{{{{kana-DEFAULTSORT|{r1}}}}}"

    return line


def repl_defaultsort(s: str) -> str:
    return "\n".join(repl_defaultsort_line(line) for line in s.splitlines())
