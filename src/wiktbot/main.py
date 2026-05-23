from wiktbot.language import repl_language
from wiktbot.reading import repl_reading
from wiktbot.trans import repl_trans
from wiktbot.wago import repl_wago


def repl(s: str) -> str:
    s = repl_reading(s)
    # s = repl_wago(s)
    # s = repl_trans(s)
    # s = repl_language(s)
    return s
