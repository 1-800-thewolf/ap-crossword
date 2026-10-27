# Crossword apworld (grid-aware fork)

This is the **Crossword** world for Archipelago, created by **jm771 (JHeard)**.
Upstream: https://github.com/jm771/apworld_crossword (`worlds/crossword`), under the MIT license in [crossword/LICENSE](crossword/LICENSE).

## What this fork changes

One backward-compatible addition: slot data gets an extra `grid` key, so web clients can draw the real puzzle.

- `puz_parser.parse_grid_layout()` reads the grid's width, height, black squares, circled squares, title and author from the `.puz`. It does **not** include solution letters.
- `CrosswordWorld.fill_slot_data()` adds the result as `slot_data["grid"]`.

Generation, items, locations and logic are unchanged. Clients that don't know about `grid` ignore it.

## Build

`dist/crossword.apworld` is this folder zipped with `crossword/` at the root. Install it by copying it into Archipelago's `custom_worlds` folder. Only the person generating the game needs it.
