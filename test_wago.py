from wago import repl_wago


def mktest(raw: str, expected: str) -> None:
    raw = raw.strip()
    expected = expected.strip()
    received = repl_wago(raw)
    assert expected == received, received


def test_repl_wago1():
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


def test_repl_wago2():
    raw = """
{{kana-DEFAULTSORT|わかれ}}
=={{ja}}==
[[カテゴリ:{{ja}}]]
===和語の漢字表記===
[[カテゴリ:{{ja}} 和語の漢字表記]]
'''[[別]]れ'''（わかれ）
#'''[[わかれ]]'''を参照。
        """
    expected = """
{{kana-DEFAULTSORT|わかれ}}
=={{ja}}==
[[カテゴリ:{{ja}}]]
==={{wago}}===
{{ja-wagokanji|わかれ}}
#{{wagokanji of|わかれ}}
        """
    mktest(raw, expected)


def test_repl_wago3():
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


# Weird bold template!
def test_repl_wago4():
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
