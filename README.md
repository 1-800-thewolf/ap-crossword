# AP Crossword on your phone

Play the Archipelago **Crossword** world in Safari or Chrome on a phone. It comes with a bulk-downloaded library of NYT-style puzzles, so you can pick one up and go. No app store and no developer account needed.

| Folder | What it is |
|---|---|
| `dist/crossword.apworld` | The Crossword world, modified to send the grid shape to clients so the phone shows the real grid. Gameplay and generation are unchanged. Source is in `apworld/`. |
| `client/index.html` | The phone/desktop web client. It's a single file with no build step, published to GitHub Pages. |
| `tools/get_crossword.bat` | Picks a random puzzle from the library (or downloads one) and writes your player YAML. It also bulk-stocks the library. |
| `library/` | Downloaded `.puz` puzzles, plus `played.json` so you don't get repeats. Local only; not in git. |
| `tools/serve_client.bat` | Serves the client to phones on your Wi-Fi. |

The Crossword world is by **jm771 (JHeard)**: https://github.com/jm771/apworld_crossword. It's MIT licensed, and this repo is a fork of it. See [apworld/README.md](apworld/README.md) for exactly what changed. The web client and tools are new code.

## One-time setup

1. Copy `dist/crossword.apworld` into `C:\ProgramData\Archipelago\custom_worlds\`. This is already done on this PC.
2. **Stock the puzzle library:** `get_crossword.bat`, option **2**, or `get_crossword.bat stock --count all`. It downloads in bulk, about 1.5 s per puzzle, and skips puzzles you already have. Stop it any time with Ctrl+C; the next run picks up where it left off.

   | Source | Puzzles | Feel |
   |---|---|---|
   | `usa`: USA Today daily | ~6,000 (back to 2010) | Easier, like NYT Mon–Wed |
   | `beq`: Brendan Emmett Quigley | ~1,930 (2008 on) | Harder, like NYT Thu–Sat; Monday themelesses |

   These are the free sources whose `robots.txt` allows automated downloads. Herbach's archive (WSJ, Universal) is linked from Crossword Fiend and Daily Crossword Links, but it blocks bots, so it isn't used. Puzzles that don't fit the Crossword world (diagramless and other odd grids) are skipped automatically.
3. **NYT Mini (optional):** free, no login. Menu option 3, or `get_crossword.bat nytm`, grabs the current Mini. NYT posts the next day's Mini in the evening, so you may get tomorrow's.
4. **Full NYT puzzles (optional):** you need your own NYT Games subscription. Menu option **7** explains how to copy your `NYT-S` cookie from a logged-in browser.

The tool needs Python 3.10–3.13. It uses `uv` if installed, otherwise the `py` launcher.

## Each game

1. **Get a puzzle:** double-click `tools/get_crossword.bat` and choose **1) Random puzzle from my library**. You can filter by source (`usa` easier, `beq` harder) and size (`mini`, `daily`, `big`). It writes `Crossword - <name>.yaml` into `C:\ProgramData\Archipelago\Players\` and marks the puzzle as played.
   - Generate uses *every* YAML in that folder, so move out any you don't want in this game.
   - Other players' YAMLs go in the same folder as usual for a multiworld.
   - Command-line use also works: `get_crossword.bat random --from beq --name Philip`, `get_crossword.bat nytm`, `get_crossword.bat uni`, `get_crossword.bat path\to\file.puz`.
2. **Generate:** Archipelago Launcher → **Generate**. Output goes to `C:\ProgramData\Archipelago\output\AP_*.zip`.
3. **Host on archipelago.gg:** go to https://archipelago.gg/uploads and upload the `AP_*.zip`. The room page shows the address, e.g. `archipelago.gg:38281`.
4. **Everyone connects as usual.** The crossword player opens **https://1-800-thewolf.github.io/ap-crossword/** on any phone or computer, then enters the room address and their slot name.
   - Shortcut: send them `https://1-800-thewolf.github.io/ap-crossword/?hostport=archipelago.gg:38281&name=SLOT` and it connects on its own.
   - In Safari, **Share → Add to Home Screen** makes it open like an app.

### The site

This repo is public on GitHub as `ap-crossword`. `.github/workflows/pages.yml` publishes the `client/` folder to GitHub Pages on every push that changes it, which takes a minute or two. Puzzles, drafts and local tool state are left out by `.gitignore`.

One-time GitHub setup: repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.

The page holds nothing secret: without a room address, slot name and room password, it's just an empty connect form. Put a password on your archipelago.gg room to keep strangers out of the game.

### Fallback: hosting on this PC

The Launcher's **Host** works, but the public https site can't connect to it, because browsers only allow secure connections from secure pages. Run `tools/serve_client.bat` instead and open the `http://192.168.x.x:8123/` address it prints. That only works for a crossword player on the same Wi-Fi. They use the server address `192.168.x.x:38281`.

## How it plays

- Hatched squares belong only to locked clues. Solve unlocked clues to send checks.
- **Clue Unlock** items reveal more clues; **Cross Letter** items fill in blue letters.
- A clue is checked automatically when every letter is right. Solved words turn green and lock.
- When every clue is solved, the client tells the server your goal is complete.
- Controls: tap a square to select it; tap it again or tap the clue bar to switch Across/Down; ‹ › jump between open clues.
- Your typed letters are saved on the device, so closing the tab or losing signal is fine. It reconnects on its own.
- **Rebus squares** (several letters in one square): type only the first letter. The world stores only the first letter.

## Notes

- The client sends Archipelago version 0.6.0 and has been tested against Archipelago 0.6.7.
- The apworld change: `puz_parser.parse_grid_layout()` plus a `grid` key in slot data (size, black squares, circled squares, title). No other behavior changed.
