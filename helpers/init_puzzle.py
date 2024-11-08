import argparse
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

PUZZLE_FILES = ("README.md",)

PY_BASE = """\
from pathlib import Path


if __name__ == "__main__":
    dataset = Path(__file__).parent.parent / Path("dataset/noahs.sqlite")

    print(f"Answer: {...}")
"""

PY_FILES = (
    "__init__.py",
    ("hod_{}_day{:02d}.py", PY_BASE),
)


def init_puzzle_day(year: int, day: int) -> None:  # noqa: D103
    year_dir = BASE_DIR / f"{year}"
    year_dir.mkdir(exist_ok=True)

    day_dir = year_dir / f"Day_{day:02d}"
    day_dir.mkdir(exist_ok=False)

    for filename in PUZZLE_FILES:
        (day_dir / filename).touch()

    for file in PY_FILES:
        if isinstance(file, str):
            filename = file.format(year, day)
            (day_dir / filename).touch()
        else:
            filename, contents = file
            filename = filename.format(year, day)
            (day_dir / filename).write_text(contents)


def main() -> None:  # noqa: D103
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int)
    parser.add_argument("day", type=int)

    args = parser.parse_args()
    init_puzzle_day(args.year, args.day)


if __name__ == "__main__":
    main()
