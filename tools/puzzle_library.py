"""
Local library of .puz files for pick-up-and-go Crossword games.

Bulk sources are limited to sites whose robots.txt allows automated downloads:
  usa  USA Today daily (archive back to 2010, easier, Mon-Wed NYT level)
  beq  Brendan Emmett Quigley (~550 puzzles from 2021 on, harder, Thu-Sat NYT level)
Downloads are spaced out (POLITE_DELAY) and never repeated.
"""
import datetime
import json
import random
import re
import time
import urllib.parse
from pathlib import Path

LIBRARY = Path(__file__).resolve().parent.parent / "library"
PLAYED_FILE = LIBRARY / "played.json"
POLITE_DELAY = 1.0
USER_AGENT = "Mozilla/5.0 (compatible; ap-crossword-library/1.0)"

SOURCES = {
    "usa": "USA Today",
    "beq": "Brendan Emmett Quigley",
}
SIZES = {"mini": (0, 8), "daily": (9, 17), "big": (18, 99)}

BEQ_SITE = "https://brendanemmettquigley.com"
USA_OLDEST = datetime.date(2010, 1, 1)


# ---------- validation ----------

def check_puz(data: bytes) -> str | None:
    """Return why a .puz can't be played in the Crossword world, or None if it's fine."""
    if len(data) < 0x34 or data[2:14] != b"ACROSS&DOWN\0":
        return "not a .puz file"
    width, height = data[0x2C], data[0x2D]
    n_clues = int.from_bytes(data[0x2E:0x30], "little")
    if not (3 <= width <= 30 and 3 <= height <= 30):
        return f"odd size {width}x{height}"
    solution = data[0x34:0x34 + width * height].decode("latin-1")
    if any(not (ch == "." or ch.isalnum()) for ch in solution):
        return "unusual grid (diagramless or special squares)"
    # Same numbering rule as the apworld's puz_parser: every word needs exactly one clue
    open_ = lambda r, c: 0 <= r < height and 0 <= c < width and solution[r * width + c] != "."
    words = sum((not open_(r, c - 1) and open_(r, c + 1)) + (not open_(r - 1, c) and open_(r + 1, c))
                for r in range(height) for c in range(width) if open_(r, c))
    if words != n_clues:
        return f"{n_clues} clues for {words} words"
    return None


def size_of(path: Path) -> str:
    with open(path, "rb") as f:
        f.seek(0x2C)
        width = f.read(1)[0]
    return next(name for name, (lo, hi) in SIZES.items() if lo <= width <= hi)


def save_if_playable(data: bytes, path: Path) -> bool:
    problem = check_puz(data)
    if problem:
        print(f"  skip {path.name}: {problem}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return True


# ---------- bulk stocking ----------

def stock(source: str, count: int | None):
    """Download up to `count` new puzzles from `source` (None = everything available)."""
    fn = {"usa": _stock_usa, "beq": _stock_beq}[source]
    print(f"Stocking {SOURCES[source]} ({'all' if count is None else count} new puzzles). Ctrl+C stops safely.")
    got = 0
    try:
        for name in fn():
            got += 1
            print(f"  [{got}] {name}", flush=True)
            if count is not None and got >= count:
                break
    except KeyboardInterrupt:
        print("  stopped.")
    print(f"Added {got} {SOURCES[source]} puzzles. Library now has {len(all_puzzles())}.")


def _stock_usa():
    from xword_dl import by_keyword
    from xword_dl.util import XWordDLException

    folder = LIBRARY / "usa"
    day = datetime.date.today()
    misses = 0
    while day >= USA_OLDEST and misses < 30:
        path = folder / f"usa-{day.isoformat()}.puz"
        if not path.exists():
            try:
                puzzle, _ = by_keyword("usa", date=day.isoformat())
                misses = 0
                if save_if_playable(puzzle.tobytes(), path):
                    yield path.name
            except XWordDLException:
                misses += 1   # no puzzle that day; a long run of misses means the archive ended
            except Exception as e:   # network hiccup: skip the day, a later run fills it in
                print(f"  {day}: {e}")
            time.sleep(POLITE_DELAY)
        day -= datetime.timedelta(days=1)


def _stock_beq():
    import requests

    folder = LIBRARY / "beq"
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    page = 1
    dead_links = 0   # files before ~#1350 (2021) were taken down; stop once we reach them
    while dead_links < 20:
        res = session.get(f"{BEQ_SITE}/wp-json/wp/v2/posts",
                          params={"per_page": 10, "page": page, "_fields": "date,title,content"}, timeout=30)
        try:
            posts = res.json()
        except ValueError:
            break
        if not isinstance(posts, list) or not posts:
            break   # past the last page
        for post in posts:
            link = re.search(r'href="(?!/solve)([^"]+\.puz)"', post["content"]["rendered"])
            if not link:
                continue
            number = re.search(r"#\s*(\d+)", post["title"]["rendered"])
            path = folder / f"beq-{number.group(1) if number else post['date'][:10]}.puz"
            if path.exists():
                continue
            puz = session.get(urllib.parse.urljoin(BEQ_SITE, link.group(1)), timeout=30)
            time.sleep(POLITE_DELAY)
            if not puz.ok:
                dead_links += 1
                continue
            dead_links = 0
            if save_if_playable(puz.content, path):
                yield path.name
        page += 1
        time.sleep(POLITE_DELAY)


# ---------- picking ----------

def all_puzzles() -> list[Path]:
    return sorted(LIBRARY.glob("*/*.puz"))


def load_played() -> set[str]:
    try:
        return set(json.loads(PLAYED_FILE.read_text()))
    except (OSError, ValueError):
        return set()


def mark_played(path: Path):
    played = load_played() | {path.relative_to(LIBRARY).as_posix()}
    PLAYED_FILE.parent.mkdir(parents=True, exist_ok=True)
    PLAYED_FILE.write_text(json.dumps(sorted(played), indent=0))


def pick_random(source: str | None = None, size: str | None = None) -> Path | None:
    played = load_played()
    candidates = [p for p in all_puzzles()
                  if p.relative_to(LIBRARY).as_posix() not in played
                  and (not source or p.parent.name == source)
                  and (not size or size_of(p) == size)]
    return random.choice(candidates) if candidates else None


def summary() -> str:
    played = load_played()
    parts = []
    for source, name in SOURCES.items():
        files = list((LIBRARY / source).glob("*.puz"))
        fresh = sum(1 for p in files if p.relative_to(LIBRARY).as_posix() not in played)
        parts.append(f"{name}: {fresh} unplayed / {len(files)}")
    return "; ".join(parts)
