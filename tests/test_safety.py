"""Test that pages with no errors do not get modified."""

from wiktbot.main import repl

CORRECT_PAGES = [
    """
=={{ja}}==
{{kana-DEFAULTSORT}}
==={{noun}}===
{{ja-noun|[[買い手]]|買手}}
#[[売買]]で[[かう|買う]]方の[[側]]。
{{スタブ|日本語}}
""",
]


def test_correct_page_remains_the_same() -> None:
    for page in CORRECT_PAGES:
        assert repl(page) == page
