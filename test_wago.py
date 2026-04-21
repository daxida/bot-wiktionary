from wago import repl_wago
from main import try_parse_header


def mktest(raw: str, expected: str) -> None:
    raw = raw.strip()
    expected = expected.strip()
    received = repl_wago(raw)
    for idx, (exp, rec) in enumerate(
        zip(expected.splitlines(), received.splitlines()),
    ):
        if exp != rec:
            print(f"First diff at {idx=}:\n{exp=}\n{rec=}")
            break
    assert expected == received, received


def test_try_parse_header() -> None:
    s = "===和語の漢字表記==="
    pos = "和語の漢字表記"
    assert try_parse_header(s, pos)


def test_repl_wago_base() -> None:
    raw = """
===和語の漢字表記===
[[Category:{{ja}} 和語の漢字表記]]
'''[[考]] え'''
#「'''[[かんがえ]]'''」参照。
"""
    expected = """
==={{wago}}===
{{ja-wagokanji|かんがえ}}
#{{wagokanji of|かんがえ}}
        """
    mktest(raw, expected)


# Only the second one is a wago redirection!
def test_repl_wago_multiple() -> None:
    raw = """
=={{L|ja}}==
[[Category:{{ja}}]]
==={{noun}}：ぎぶつ===
{{head|jpn|noun|sort=きふつ ぎぶつ|head=[[偽]][[物]]}}（ぎぶつ）
#[[にせもの]]。
===={{pron}}====
;ぎ↗ぶつ
==={{noun}}：にせもの===
[[カテゴリ:{{ja}} 和語の漢字表記]]
{{jachars}}（にせもの）
#「'''[[にせもの]]'''」を参照。
"""
    expected = """
=={{L|ja}}==
[[Category:{{ja}}]]
==={{noun}}：ぎぶつ===
{{head|jpn|noun|sort=きふつ ぎぶつ|head=[[偽]][[物]]}}（ぎぶつ）
#[[にせもの]]。
===={{pron}}====
;ぎ↗ぶつ
==={{wago}}===
{{ja-wagokanji|にせもの}}
#{{wagokanji of|にせもの}}
        """
    mktest(raw, expected)


def test_repl_wago1():
    raw = """
=={{ja}}==
[[カテゴリ:{{ja}}]]
===和語の漢字表記===
[[カテゴリ:{{ja}} 和語の漢字表記]]
'''[[別]]れ'''（わかれ）
#'''[[わかれ]]'''を参照。
        """
    expected = """
=={{ja}}==
[[カテゴリ:{{ja}}]]
==={{wago}}===
{{ja-wagokanji|わかれ}}
#{{wagokanji of|わかれ}}
        """
    mktest(raw, expected)


def test_repl_wago2():
    raw = """
{{DEFAULTSORT:こころのこり}}
=={{ja}}==
[[category:{{ja}}]]
===和語の漢字表記===
[[Category:{{ja}} 和語の漢字表記]]
'''[[心]] [[のこり|残り]]'''（こころのこり）
#'''[[こころのこり]]'''を参照
        """
    expected = """
{{DEFAULTSORT:こころのこり}}
=={{ja}}==
[[category:{{ja}}]]
==={{wago}}===
{{ja-wagokanji|こころのこり}}
#{{wagokanji of|こころのこり}}
        """
    mktest(raw, expected)


# We don't delete categories after the reading
def test_repl_wago_untouched_after_reading() -> None:
    raw = """
===和語の漢字表記===
{{lang|ja|'''[[奨]]める'''}}（すすめる）
#'''[[すすめる]]'''　参照
[[カテゴリ:{{ja}} 和語の漢字表記]]
"""
    expected = """
==={{wago}}===
{{ja-wagokanji|すすめる}}
#{{wagokanji of|すすめる}}
[[カテゴリ:{{ja}} 和語の漢字表記]]
"""
    mktest(raw, expected)


def test_repl_wago_weird_template():
    raw = """
{{DEFAULTSORT:おもい}}
=={{ja}}==
[[Category:{{ja}}]]

===和語の漢字表記===
[[Category:{{ja}} 和語の漢字表記]]
'''{{l|ja|想}}い'''

# 「'''[[おもい]]'''」を参照。
        """
    expected = """
{{DEFAULTSORT:おもい}}
=={{ja}}==
[[Category:{{ja}}]]

==={{wago}}===
{{ja-wagokanji|おもい}}
#{{wagokanji of|おもい}}
        """
    mktest(raw, expected)
