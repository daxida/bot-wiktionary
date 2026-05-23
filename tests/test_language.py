from wiktbot.language import repl_language


def mktest(raw: str, expected: str) -> None:
    raw = raw.strip()
    expected = expected.strip()
    received = repl_language(raw)
    assert expected == received, received


def test_trans_base() -> None:
    raw = """
=={{ja}}==
==日本語==
=={{zh}}==
"""
    expected = """
=={{L|ja}}==
=={{L|ja}}==
=={{L|zh}}==
        """
    mktest(raw, expected)
