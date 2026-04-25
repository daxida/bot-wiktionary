from wiktbot.reading import repl_reading
from wiktbot.wago import repl_wago
from wiktbot.trans import repl_trans


def repl(s: str) -> str:
    s = repl_reading(s)
    s = repl_wago(s)
    s = repl_trans(s)
    return s
