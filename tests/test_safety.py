"""Test that pages with no errors do not get modified."""

from wiktbot.main import repl

CORRECT_PAGES = [
    """
=={{L|ja}}==
{{kana-DEFAULTSORT}}
==={{noun}}===
{{ja-noun|[[買い手]]|買手}}
#[[売買]]で[[かう|買う]]方の[[側]]。
{{スタブ|日本語}}
""",
    # Don't change the section for Chinese...
    """
=={{L|zh}}==
==={{noun}}===
[[Category:{{zh}}_{{noun}}|lan2]]
[[Category:{{zh}}_植物|lan2]]
[[Category:{{zh}}_色|lan2]]
#（植物、染料）{{ふりがな|藍|あい}}。
    """,
    # Don't change templates for ancient Japanese...
    """
=={{L|ojp}}==
==={{verb}}===
{{head|ojp|verb}}【[[離]]る】
    """,
]


def test_correct_page_remains_the_same() -> None:
    for page in CORRECT_PAGES:
        page = page.strip()
        assert repl(page) == page
