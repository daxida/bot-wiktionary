"""Fix DEFAULTSORT template.

{{DEFAULTSORT:うつる}} becomes {{kana-DEFAULTSORT|うつる}}
"""

import re


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

    return line


def repl_defaultsort(s: str) -> str:
    return "\n".join(repl_defaultsort_line(line) for line in s.splitlines())
