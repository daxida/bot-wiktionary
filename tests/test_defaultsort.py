from wiktbot.defaultsort import repl_defaultsort


def mktest(raw: str, expected: str) -> None:
    raw = raw.strip()
    expected = expected.strip()
    received = repl_defaultsort(raw)
    assert expected == received, received


def test_trans_base() -> None:
    raw = """
{{DEFAULTSORT:うつる}}
"""
    expected = """
{{kana-DEFAULTSORT|うつる}}
        """
    mktest(raw, expected)


def test_trans_with_pagename() -> None:
    raw = """
{{DEFAULTSORT:かいう {{PAGENAME}}}}
"""
    expected = """
{{kana-DEFAULTSORT|かいう}}
        """
    mktest(raw, expected)
