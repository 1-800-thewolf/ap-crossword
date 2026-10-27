"""
Download a crossword (NYT or other outlets via xword-dl) and turn it into an
Archipelago player YAML for the Crossword world.

Run with no arguments for a menu, or e.g.:
    get_crossword.py random                   random unplayed puzzle from the library
    get_crossword.py random --from beq --size daily
    get_crossword.py stock --count 500        bulk download into the library (usa + beq)
    get_crossword.py stock beq --count all
    get_crossword.py nytm                     today's NYT Mini (free)
    get_crossword.py uni                      today's Universal (free)
    get_crossword.py path/to/puzzle.puz       a .puz you already have
    get_crossword.py nyt --date 2024-05-01    NYT (needs subscription login)
    get_crossword.py --nyt-login              store your NYT-S cookie
"""
import argparse
import base64
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

import puzzle_library

HERE = Path(__file__).resolve().parent
SETTINGS_FILE = HERE / "settings.json"
DEFAULT_PLAYERS_DIRS = [Path(r"C:\ProgramData\Archipelago\Players"), Path.home() / "Archipelago" / "Players"]

FREE_SOURCES = {
    "uni": "Universal",
    "usa": "USA Today",
    "wp": "Washington Post",
    "lat": "Los Angeles Times",
    "tny": "New Yorker",
    "nd": "Newsday",
}
NYT_SOURCES = {"nyt": "New York Times", "nytm": "New York Times Mini"}
NYT_MINI_TODAY_URL = "https://www.nytimes.com/svc/crosswords/v6/puzzle/mini.json"


def load_settings() -> dict:
    try:
        return json.loads(SETTINGS_FILE.read_text())
    except (OSError, ValueError):
        return {}


def save_settings(settings: dict):
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2))


def xword_dl_cmd() -> list[str]:
    exe = shutil.which("xword-dl", path=str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""))
    if not exe:
        sys.exit("xword-dl is not installed. Run get_crossword.bat, or: pip install xword-dl")
    return [exe]


def download(source: str, date: str | None) -> Path:
    out = Path(tempfile.mkdtemp()) / "puzzle.puz"
    cmd = xword_dl_cmd() + [source, "-o", str(out)]
    if date:
        cmd += ["--date", date]
    print(f"Downloading {NYT_SOURCES.get(source) or FREE_SOURCES.get(source) or source}"
          f"{' for ' + date if date else ''}...", flush=True)
    result = subprocess.run(cmd)
    if result.returncode != 0 or not out.exists():
        if source in NYT_SOURCES:
            print("\nNYT download failed. NYT needs your subscription login. Run this tool's"
                  " 'Set up NYT login' option (or --nyt-login) and paste your NYT-S cookie.")
        sys.exit(1)
    return out


def download_free_mini() -> tuple[Path, str]:
    """Today's NYT Mini is free to play on nytimes.com, so this needs no login."""
    import types
    import requests
    from xword_dl.downloader.newyorktimesdownloader import NewYorkTimesDownloader

    print("Downloading today's New York Times Mini...", flush=True)
    res = requests.get(NYT_MINI_TODAY_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    res.raise_for_status()
    # Reuse xword-dl's NYT JSON -> .puz conversion (handles circles and rebus squares)
    data = res.json()
    puzzle = NewYorkTimesDownloader.parse_xword(types.SimpleNamespace(date=None), data)
    out = Path(tempfile.mkdtemp()) / "puzzle.puz"
    puzzle.save(str(out))
    # NYT posts the next day's Mini the evening before, so use its own date
    return out, data.get("publicationDate") or datetime.date.today().isoformat()


def nyt_login():
    print("""
NYT puzzles need your own NYT Games subscription. xword-dl uses the NYT-S cookie
from a browser where you're logged in to nytimes.com:

  1. On a computer, log in at https://www.nytimes.com/crosswords
  2. Open developer tools (F12) > Application (Chrome/Edge) or Storage (Firefox)
     > Cookies > https://www.nytimes.com
  3. Copy the value of the cookie named NYT-S
""")
    token = input("Paste NYT-S value (blank to cancel): ").strip()
    if not token:
        return
    # Same config file xword-dl reads: ~/.config/xword-dl/xword-dl.yaml, section nyt
    from xword_dl.util.utils import update_config_file
    update_config_file("nyt", {"NYT-S": token})
    print("Saved. NYT downloads should work now.\n")


def describe_puz(data: bytes) -> tuple[int, int, str, bool]:
    width, height = data[0x2C], data[0x2D]
    strings = data[0x34 + 2 * width * height:]
    title = strings.split(b"\0", 1)[0].decode("latin-1")
    return width, height, title, b"GRBS" in strings


def write_yaml(puz: Path, slot_name: str, players_dir: Path, label: str) -> Path:
    data = puz.read_bytes()
    width, height, title, has_rebus = describe_puz(data)
    if not width or not height:
        sys.exit(f"{puz} doesn't look like a .puz file.")
    contents = base64.b64encode(zlib.compress(data, 9)).decode("ascii")

    players_dir.mkdir(parents=True, exist_ok=True)
    safe_label = "".join(ch if ch.isalnum() or ch in " -_" else "_" for ch in label).strip()
    path = players_dir / f"Crossword - {safe_label}.yaml"
    path.write_text(f"""# {title or label} ({width}x{height})
# Made by get_crossword.py. Option docs: see the Crossword apworld Options.py
name: {slot_name}
game: Crossword
description: {json.dumps(title or label)}
requires:
  version: 0.6.0
Crossword:
  # Percent of clues visible at the start
  starting_percent: 10
  # Over-allocation of Clue Unlock value (100+); higher = clues unlock sooner
  clue_alloc_percent: 120
  # Percent of item rewards that are Clue Unlocks (the rest are Cross Letters)
  clue_item_fraction: 20
  # in_puzzle: letters at crossings only; all: any letter
  cross_letter_generation: in_puzzle
  cross_letter_alloc_percent: 100
  puz_file_contents: "{contents}"
""", encoding="utf-8")

    print(f"\nWrote {path}")
    print(f"  Puzzle: {title or label}, {width}x{height}, slot name '{slot_name}'")
    if has_rebus:
        print("  Note: this puzzle has rebus squares. Type only the FIRST letter in those squares.")
    others = [p.name for p in players_dir.glob("*.yaml") if p != path]
    if others:
        print(f"  Heads up: Generate uses every YAML in {players_dir}. Also there: {', '.join(others)}")
    return path


def find_players_dir(settings: dict) -> Path:
    if settings.get("players_dir"):
        return Path(settings["players_dir"])
    for d in DEFAULT_PLAYERS_DIRS:
        if d.exists():
            return d
    return HERE / "Players"


def menu(settings: dict) -> argparse.Namespace:
    print("Crossword puzzle for Archipelago\n")
    print(f"  Library: {puzzle_library.summary()}\n")
    print("  1) Random puzzle from my library")
    print("  2) Stock up the library (bulk download)")
    print("  3) Today's NYT Mini (free, no login)")
    print("  4) Today's crossword from another outlet (Universal, USA Today, ...)")
    print("  5) A .puz file I already have")
    print("  6) NYT crossword (needs subscription login)")
    print("  7) Set up NYT login")
    choice = input("\nChoose 1-7: ").strip()
    ns = argparse.Namespace(what=[], date=None, nyt_login=False, name=None, size=None, lib_from=None, count=None)
    if choice == "1":
        ns.what = ["random"]
        ns.lib_from = input("Source: usa (easier), beq (harder), tnym (minis), blank = any: ").strip() or None
        ns.size = input("Size: mini, daily, big, blank = any: ").strip() or None
    elif choice == "2":
        ns.what = ["stock"] + (input("Sources: usa, beq, tnym, blank = all: ").split() or [])
        ns.count = input("How many new puzzles per source (number or 'all') [200]: ").strip() or "200"
        return ns
    elif choice == "3":
        ns.what = ["nytm"]
    elif choice == "4":
        for key, name in FREE_SOURCES.items():
            print(f"  {key:5} {name}")
        ns.what = [input("Source code (e.g. uni): ").strip() or "uni"]
        ns.date = input("Date (blank for latest): ").strip() or None
    elif choice == "5":
        ns.what = [input("Path to .puz file: ").strip().strip('"')]
    elif choice == "6":
        ns.what = ["nyt"]
        ns.date = input("Date (blank for today, e.g. 2024-05-01): ").strip() or None
    elif choice == "7":
        ns.nyt_login = True
    else:
        sys.exit("Nothing chosen.")
    if not ns.nyt_login:
        default = settings.get("slot_name", "Crossword")
        ns.name = input(f"Slot name [{default}]: ").strip() or default
    return ns


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("what", nargs="*",
                        help="random | stock [usa beq] | an xword-dl source (nytm, uni, usa, ...) | a .puz path")
    parser.add_argument("--date", help="puzzle date, e.g. 2024-05-01")
    parser.add_argument("--name", help="Archipelago slot name for the YAML")
    parser.add_argument("--players-dir", help="where to write the YAML (default: Archipelago Players folder)")
    parser.add_argument("--nyt-login", action="store_true", help="store your NYT-S cookie for NYT downloads")
    parser.add_argument("--from", dest="lib_from", choices=list(puzzle_library.SOURCES), help="random: library source")
    parser.add_argument("--size", choices=list(puzzle_library.SIZES), help="random: puzzle size")
    parser.add_argument("--count", help="stock: new puzzles per source, or 'all' (default 200)")
    args = parser.parse_args()
    settings = load_settings()
    if not args.what and not args.nyt_login:
        picked = menu(settings)
        for key, value in vars(picked).items():
            if value is not None and value != []:
                setattr(args, key, value)
    if args.players_dir:
        settings["players_dir"] = args.players_dir

    if args.nyt_login:
        return nyt_login()

    if args.what[0] == "stock":
        count = None if str(args.count).lower() == "all" else int(args.count or 200)
        for source in args.what[1:] or list(puzzle_library.SOURCES):
            puzzle_library.stock(source, count)
        return

    slot_name = (args.name or settings.get("slot_name") or "Crossword")[:16]
    settings["slot_name"] = slot_name
    save_settings(settings)

    source = args.what[0]
    if source == "random":
        puz = puzzle_library.pick_random(args.lib_from, args.size)
        if not puz:
            sys.exit("No unplayed puzzles match. Stock up the library first (menu option 2).")
        label = f"{puzzle_library.SOURCES[puz.parent.name]} {puz.stem.split('-', 1)[1]}"
        write_yaml(puz, slot_name, find_players_dir(settings), label)
        puzzle_library.mark_played(puz)
        print(f"\nLibrary: {puzzle_library.summary()}")
        print("Next: Archipelago Launcher > Generate, then host the game (see README).")
        return
    if Path(source).suffix.lower() == ".puz":
        puz = Path(source)
        if not puz.exists():
            sys.exit(f"File not found: {puz}")
        label = puz.stem
    elif source == "nytm" and not args.date:
        puz, date = download_free_mini()
        label = f"NYT Mini {date}"
    else:
        puz = download(source, args.date)
        name = {**NYT_SOURCES, **FREE_SOURCES}.get(source, source)
        label = f"{name} {args.date or datetime.date.today().isoformat()}"

    write_yaml(puz, slot_name, find_players_dir(settings), label)
    print("\nNext: Archipelago Launcher > Generate, then host the game (see README).")


if __name__ == "__main__":
    main()
