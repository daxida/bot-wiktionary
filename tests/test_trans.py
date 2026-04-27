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


def test_repl_trans_base() -> None:
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


def test_repl_trans_already_correct() -> None:
    raw = """
===={{trans}}====
*{{en}}: {{t|en|archives}}, {{t|en|archive}}
"""
    expected = """
===={{trans}}====
*{{en}}: {{t|en|archives}}, {{t|en|archive}}
        """
    mktest(raw, expected)
