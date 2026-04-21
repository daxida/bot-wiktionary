"""Test that pages with no errors do not get modified."""

from main import repl_ja_template
from wago import repl_wago

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
        assert repl_ja_template(page) == page
        assert repl_wago(page) == page
