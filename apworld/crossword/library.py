"""
Picks a random unplayed .puz from the host's crossword library (one subfolder per source,
e.g. library/usa, library/beq). played.json in the library root is shared with the
library tools, so puzzles aren't repeated across games.
"""
import json
import os
import threading
from pathlib import Path

SIZES = {"mini": (0, 8), "daily": (9, 17), "big": (18, 99)}
PLAYED_FILE = "played.json"

# Puzzles chosen by other Crossword slots in this generation, so two slots don't share one
_picked_this_run: set[str] = set()
# generate_output runs for all worlds in parallel threads
_played_lock = threading.Lock()


def load_played(library: Path) -> set[str]:
    try:
        return set(json.loads((library / PLAYED_FILE).read_text()))
    except (OSError, ValueError):
        return set()


def mark_played(library: Path, rel_path: str):
    with _played_lock:
        played = load_played(library) | {rel_path}
        tmp = library / (PLAYED_FILE + ".tmp")
        tmp.write_text(json.dumps(sorted(played), indent=0))
        os.replace(tmp, library / PLAYED_FILE)


def width_of(path: Path) -> int:
    with open(path, "rb") as f:
        f.seek(0x2C)
        return f.read(1)[0]


def pick_puzzle(library: Path, source: str, size: str, rng) -> tuple[Path, str]:
    """Return (path, path relative to the library) of a random unplayed puzzle."""
    if not library.is_dir():
        raise FileNotFoundError(f"Crossword library folder not found: {library}. "
                                f"Set crossword_options.library_path in host.yaml.")
    folders = sorted(d for d in library.iterdir() if d.is_dir()) if source == "any" else [library / source]
    played = load_played(library) | _picked_this_run
    lo, hi = SIZES.get(size, (0, 99))
    unplayed = [p for folder in folders for p in sorted(folder.glob("*.puz"))
                if p.relative_to(library).as_posix() not in played]
    # Shuffle, then read sizes only until one fits; opening thousands of files up front is slow
    rng.shuffle(unplayed)
    path = next((p for p in unplayed if lo <= width_of(p) <= hi), None)
    if path is None:
        raise FileNotFoundError(f"No unplayed '{size}' puzzles from '{source}' in {library}. "
                                f"Stock up with get_crossword.bat or change puzzle_source/puzzle_size.")
    rel = path.relative_to(library).as_posix()
    _picked_this_run.add(rel)
    return path, rel
