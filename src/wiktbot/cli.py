import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

from wiktbot.main import repl
from wiktbot.bot import run


Cmd = Literal["run", "repl", "snapshot"]


@dataclass
class Args:
    ipath: Path
    opath: Path
    command: Cmd
    fixture_dir: Path | None = None
    max_pages: int = 100


def cmd_repl(args: Args) -> None:
    print(f"Reading @ {args.ipath}")
    text = args.ipath.read_text(encoding="utf-8")
    # Overwrite with stripped contents for simpler diffs
    args.ipath.write_text(text.strip(), encoding="utf-8")

    result = repl(text)
    args.opath.write_text(result, encoding="utf-8")
    print(f"Writing @ {args.opath}")


def cmd_snapshot(args: Args) -> None:
    assert args.fixture_dir is not None
    args.fixture_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d")

    input_text = args.ipath.read_text(encoding="utf-8") if args.ipath.exists() else ""
    output_text = args.opath.read_text(encoding="utf-8") if args.opath.exists() else ""

    dest = args.fixture_dir / f"test_{now}.txt"
    dest.write_text(f"{input_text}\n</>\n{output_text}", encoding="utf-8")
    print(f"Snapshot written @ {dest}")


def parse_args() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", default="input.txt", help="Input file (default: input.txt)"
    )
    parser.add_argument(
        "--output", default="output.txt", help="Output file (default: output.txt)"
    )

    subparsers = parser.add_subparsers(dest="command")
    run = subparsers.add_parser("run", help="Run the bot for scanning")
    run.add_argument("max_pages", type=int, nargs="?", default=100)

    subparsers.add_parser("repl", help="Process input.txt and write output.txt")

    snap = subparsers.add_parser(
        "snapshot", help="Copy input/output to a fixture folder"
    )
    snap.add_argument(
        "fixture_dir",
        nargs="?",
        default="tests/fixtures",
        help="Destination folder (default: tests/fixtures)",
    )

    args = parser.parse_args()

    fixture_dir = None
    if _fixture_dir := getattr(args, "fixture_dir", None):
        fixture_dir = Path(_fixture_dir)

    max_pages = 100
    if _max_pages := getattr(args, "max_pages", None):
        max_pages = _max_pages

    return Args(
        ipath=Path(args.input),
        opath=Path(args.output),
        command=args.command,
        fixture_dir=fixture_dir,
        max_pages=max_pages,
    )


def main() -> None:
    args = parse_args()

    match args.command:
        case "snapshot":
            cmd_snapshot(args)
        case "repl":
            cmd_repl(args)
        case "run":
            run(args.max_pages)


if __name__ == "__main__":
    main()
