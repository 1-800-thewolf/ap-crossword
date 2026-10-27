# Crossword apworld (grid-aware fork)

This is the **Crossword** world for Archipelago, created by **jm771 (JHeard)**.
Upstream: https://github.com/jm771/apworld_crossword (`worlds/crossword`), under the MIT license in [crossword/LICENSE](crossword/LICENSE).

## What this fork changes

Two backward-compatible additions. Items, locations and logic are unchanged, and YAMLs written for the original still work.

**1. Grid layout in slot data.** Slot data gets an extra `grid` key, so web clients can draw the real puzzle.
- `puz_parser.parse_grid_layout()` reads the grid's width, height, black squares, circled squares, title and author from the `.puz`. It does **not** include solution letters.
- `CrosswordWorld.fill_slot_data()` adds the result as `slot_data["grid"]`. Clients that don't know about it ignore it.

**2. Random library puzzles.** `puz_file_path` and `puz_file_contents` are now optional. With neither set, `generate_early` picks a random unplayed `.puz` from the host's library (`library.py`).
- New options: `puzzle_source` (`any`, `usa`, `beq` or any library subfolder name) and `puzzle_size` (`mini`, `daily`, `big`, `any`; default `daily`).
- The library folder is a host setting, `crossword_options.library_path` in `host.yaml` (default `crossword_library`).
- Picked puzzles are added to `played.json` in the library once generation succeeds, and two Crossword slots in one seed never get the same puzzle.
- The spoiler log names the puzzle.

## Build

`dist/crossword.apworld` is this folder zipped with `crossword/` at the root. Install it by copying it into Archipelago's `custom_worlds` folder. Only the person generating the game needs it.
