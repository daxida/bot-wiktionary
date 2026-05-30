from wiktbot.trans import repl_trans


def mktest(raw: str, expected: str) -> None:
    raw = raw.strip()
    expected = expected.strip()
    received = repl_trans(raw)
    for idx, (exp, rec) in enumerate(
        zip(expected.splitlines(), received.splitlines()),
    ):
        if exp != rec:
            print(f"First diff at {idx=}:\n{exp=}\n{rec=}")
            break
    assert expected == received, received


def test_trans_base() -> None:
    raw = """
===={{trans}}==== 
*{{de}}: [[Lebenslauf]]
*{{en}}: [[history]], [[record]], [[career]]
*{{fr}}: [[carrière]]
"""
    expected = """
===={{trans}}==== 
*{{T|de}}: {{t|de|Lebenslauf}}
*{{T|en}}: {{t|en|history}}, {{t|en|record}}, {{t|en|career}}
*{{T|fr}}: {{t|fr|carrière}}
        """
    mktest(raw, expected)


def test_trans_no_space() -> None:
    raw = """
===={{trans}}====
*{{en}}:[[sister-in-law]]
"""
    expected = """
===={{trans}}====
*{{T|en}}: {{t|en|sister-in-law}}
        """
    mktest(raw, expected)


def test_trans_already_correct() -> None:
    raw = """
===={{trans}}====
*{{T|en}}: {{t|en|archives}}, {{t|en|archive}}
"""
    expected = """
===={{trans}}====
*{{T|en}}: {{t|en|archives}}, {{t|en|archive}}
        """
    mktest(raw, expected)


def test_trans_both_bold() -> None:
    raw = """
===={{trans}}====
{{top}}
*[[{{it}}]]: [[prova]]
    """
    expected = """
===={{trans}}====
{{top}}
*{{T|it}}: {{t|it|prova}}
        """
    mktest(raw, expected)


def test_trans_alt_dots() -> None:
    raw = """
===={{trans}}====
*{{en}}：[[replacement]]
    """
    expected = """
===={{trans}}====
*{{T|en}}: {{t|en|replacement}}
        """
    mktest(raw, expected)


def test_trans_raw_lang() -> None:
    raw = """
===={{trans}}====
*英語: [[homeomorphism]]
"""
    expected = """
===={{trans}}====
*{{T|en}}: {{t|en|homeomorphism}}
"""
    mktest(raw, expected)
