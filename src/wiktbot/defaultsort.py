"""Fix DEFAULTSORT template.

{{DEFAULTSORT:うつる}} becomes {{kana-DEFAULTSORT|うつる}}
"""

import re


def repl_defaultsort_line(line: str) -> str:
    if m := re.match(r"{{DEFAULTSORT:(.*)}}", line):
        readings = m.group(1).split(" ")
        # Only replace if there is exactly one reading (for now)
        if len(readings) == 1:
            reading = readings[0]
            return f"{{{{kana-DEFAULTSORT|{reading}}}}}"
    return line


def repl_defaultsort(s: str) -> str:
    return "\n".join(repl_defaultsort_line(line) for line in s.splitlines())
