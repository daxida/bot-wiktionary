from wiktbot.defaultsort import repl_defaultsort


def mktest(raw: str, expected: str) -> None:
    raw = raw.strip()
    expected = expected.strip()
    received = repl_defaultsort(raw)
    assert expected == received, received


def test_defaultsort_base() -> None:
    raw = """
{{DEFAULTSORT:うつる}}
"""
    expected = """
{{kana-DEFAULTSORT|うつる}}
        """
    mktest(raw, expected)


def test_defaultsort_pagename() -> None:
    raw = """
{{DEFAULTSORT:かいう {{PAGENAME}}}}
"""
    expected = """
{{kana-DEFAULTSORT|かいう}}
        """
    mktest(raw, expected)


def test_defaultsort_preferred_choice() -> None:
    raw = """
{{DEFAULTSORT:ほんふん ほんぶん}}
{{DEFAULTSORT:しゆうそく じゅうぞく}}
{{DEFAULTSORT:ゆ ゅ}}
"""
    expected = """
{{kana-DEFAULTSORT|ほんぶん}}
{{kana-DEFAULTSORT|じゅうぞく}}
{{kana-DEFAULTSORT|ゅ}}
        """
    mktest(raw, expected)


def test_defaultsort_unknown() -> None:
    raw = """
{{DEFAULTSORT:a potato}}
"""
    expected = """
{{DEFAULTSORT:a potato}}
        """
    mktest(raw, expected)
