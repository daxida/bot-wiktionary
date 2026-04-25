from pathlib import Path
from wiktbot.main import repl


def test_fixtures() -> None:
    fixture_dir = Path("tests/fixtures")
    fixture_files = sorted(fixture_dir.glob("test_*.txt"))
    assert fixture_files, "No fixture files found in fixtures/"

    for fixture_file in fixture_files:
        content = fixture_file.read_text(encoding="utf-8")
        input_text, expected = content.split("</>", maxsplit=1)

        input_text = input_text.strip()
        expected = expected.strip()

        result = repl(input_text)
        assert result == expected
