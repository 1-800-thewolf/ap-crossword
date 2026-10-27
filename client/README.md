# AP Crossword

A web client for the **Crossword** world in [Archipelago](https://archipelago.gg) multiworld randomizers. Play your crossword slot in any phone or desktop browser, live with everyone else in the multiworld. Nothing to install.

**Play:** https://1-800-thewolf.github.io/ap-crossword/

## How to play

1. Open the page and enter the room's server (e.g. `archipelago.gg:38281`), your slot name and the password, if any.
2. Solve the unlocked clues. Each solved clue sends a check to the multiworld.
3. **Clue Unlock** items from other players reveal more clues, and **Cross Letter** items fill in letters, shown in blue.
4. Solve every clue to complete your goal.

Hatched squares belong only to clues that are still locked. To switch between Across and Down, tap the selected square again or tap the clue bar. ‹ › jump between open clues.

## Share a link that connects right away

```
https://1-800-thewolf.github.io/ap-crossword/?hostport=archipelago.gg:38281&name=SlotName
```

You can add `&password=...` if the room has one, but anyone with the link then sees it.

## Notes

- **Servers:** works with rooms hosted on archipelago.gg. A server on someone's own PC usually only offers plain `ws://` connections, which browsers block from an `https://` page.
- **Grid vs. clue cards:** you see the full grid when the game was generated with the grid-aware version of the Crossword apworld. With the original apworld, each clue appears as its own row of boxes instead.
- **Saved progress:** your letters are saved in this browser only. Nothing is sent anywhere except to the Archipelago server you connect to.
- **Rebus squares:** type the first letter only.
