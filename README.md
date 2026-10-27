# AP Crossword

Play the **Crossword** world in an Archipelago multiworld from your phone's browser. No app, no install.

**▶ Play: https://1-800-thewolf.github.io/ap-crossword/**

## How the Crossword world works

The Crossword world turns a real crossword puzzle into an Archipelago game:

- **Locations = clues.** Every clue you solve is a check, and it can send an item to anyone in the multiworld.
- **Items = help for your puzzle.** Two kinds are shuffled into the multiworld, so other players find most of them in their games:
  - **Clue Unlock:** reveals more clues. You start with about 10% of the clues visible.
  - **Cross Letter:** fills in letters on the grid (shown in blue).
- **Goal:** solve every clue.

You'll usually run out of open clues and wait on your friends' progress, the same way a locked area in any other Archipelago game waits on items.

## Connecting from your phone

You need three things from your host: the **room address** (e.g. `archipelago.gg:38281`), your **slot name**, and the **room password**, if there is one.

1. Open **https://1-800-thewolf.github.io/ap-crossword/** in Safari (iPhone) or Chrome (Android).
2. Enter the **port** from the room page; the address is already filled in as `archipelago.gg`. Then add your slot name and password. Next time, the page remembers the address, port and slot you last used, so you'll usually only need to change the port for a new room. If you play on someone's own server, type its address once and it's remembered too.
3. Tap **Connect**. The grid appears, and the dot at the top left turns green when you're connected.

**Faster:** your host can send a link that fills everything in and connects right away:

```
https://1-800-thewolf.github.io/ap-crossword/?hostport=archipelago.gg:38281&name=YourSlot
```

**Make it feel like an app:** in Safari, **Share → Add to Home Screen**; in Chrome, **⋮ → Add to Home screen**. The page also remembers the last server and slot you used.

### Playing

- **Tap a square** to select it. **Tap it again**, or tap the clue bar, to switch between Across and Down. Use **‹ ›** to jump between open clues.
- Type with the **on-screen keyboard** at the bottom. It's built in, so your phone's keyboard won't cover the grid.
- A clue is **checked automatically** once every letter is right. It turns green and locks.
- **Hatched squares** belong only to clues that are still locked. You can still fill them through a crossing clue that's open.
- **Notifications** pop up when items arrive and new clues unlock.
- **Rebus squares** (several letters in one square): type only the first letter.
- On a computer, a physical keyboard works too: letters, Backspace, arrow keys, Tab for the next clue, Space to switch direction.

### Signal drops and closed tabs

Your letters are saved on your phone. If the phone sleeps, you switch apps or you lose signal, the page reconnects on its own when you come back; the dot turns yellow while it retries. Anything you solved while offline is sent once you're back. Letters are saved per phone and browser, so switching devices mid-game keeps your solved clues (the server tracks those) but not half-filled answers.

### Can't connect?

- **"Couldn't connect":** check the room address and port. Rooms on archipelago.gg get a new port when they restart after being idle, so check the room page for the current one.
- **"InvalidSlot":** the slot name has to match exactly, including capital letters.
- **Host runs the server on their own PC:** this site can't connect to that. Browsers only allow a secure (`https`) page to make secure connections, and a home server usually doesn't offer them. Ask the host to use archipelago.gg, or see [Hosting on your own PC](#hosting-on-your-own-pc).
- **The puzzle shows rows of boxes instead of a grid:** the game was generated with the original Crossword apworld. It's fully playable, just without the grid view. Hosts: use the apworld from this repo to get the grid.

---

## For the host

Set up everything else the usual way. The crossword only adds a YAML.

1. **Install the apworld once:** copy [`dist/crossword.apworld`](dist/crossword.apworld) into your Archipelago `custom_worlds` folder. Only the person generating needs it; players never do.
2. **Make the crossword YAML.** On Windows, run `tools/get_crossword.bat` → **1) Random puzzle from my library**. It writes the YAML into your Archipelago `Players` folder and marks the puzzle as played, so you won't get repeats. Or write one yourself with `puz_file_path` (or `puz_file_contents`) pointing at any `.puz` crossword.
3. **Generate** as usual, alongside everyone else's YAMLs.
4. **Upload** the `AP_*.zip` at https://archipelago.gg/uploads and create a room.
5. **Send the crossword player** the play link with `?hostport=archipelago.gg:PORT&name=SLOT` filled in.

Put a password on the room if you don't want strangers wandering in.

### Puzzle library

`tools/get_crossword.bat` also bulk-downloads puzzles into `library/` (menu option **2**, or `get_crossword.bat stock --count all`). It skips puzzles you already have and filters out grids the world can't handle. Ctrl+C is safe; the next run picks up where it stopped.

| Source | Puzzles | Feel |
|---|---|---|
| `usa`: USA Today daily | ~6,000 (2010 on) | Easier, like NYT Mon–Wed |
| `beq`: Brendan Emmett Quigley | ~1,930 (2008 on) | Harder, like NYT Thu–Sat |

Only sources whose `robots.txt` allows automated downloads are used. Puzzles stay on your PC and aren't committed to this repo. The tool can also grab today's free NYT Mini (`nytm`), today's puzzle from other outlets (e.g. `uni`), or NYT puzzles if you have a subscription. It needs Python 3.10–3.13 and uses `uv` if it's installed.

### Hosting on your own PC

The public site can't reach a home server (see [Can't connect?](#cant-connect)). For players on the same Wi-Fi as the host, run `tools/serve_client.bat` and have them open the `http://192.168.x.x:8123/` address it prints, with the server address `192.168.x.x:38281`.

---

## About this repo

| Path | What it is |
|---|---|
| `client/` | The web client: a single `index.html` with no build step. GitHub Pages publishes it automatically on every push that changes it. |
| `apworld/`, `dist/` | The grid-aware fork of the Crossword world, as source and as the built `.apworld`. |
| `tools/` | The YAML maker, puzzle library and local web server. |

**Credits:** the Crossword world is by **jm771 (JHeard)**: https://github.com/jm771/apworld_crossword, MIT licensed. This fork adds one backward-compatible `grid` entry to slot data so clients can draw the puzzle; see [apworld/README.md](apworld/README.md). The web client and tools are new code. Tested with Archipelago 0.6.7 locally and 0.6.8 on archipelago.gg.
