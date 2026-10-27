from dataclasses import dataclass

from Options import Choice, FreeText, PerGameCommonOptions, Range, TextChoice

class FilePath(FreeText):
    """
    Use this exact .puz crossword file instead of a library puzzle.
    The path is on the computer that generates the game.
    Use at most one of puz_file_path and puz_file_contents; leave both empty to use the library.
    """
    display_name = "Puzzle File Path"

class Base64FileContents(FreeText):
    """
    A .puz crossword embedded in the YAML (zlib-compressed, then base64).
    get_crossword.bat writes this for you; there's no need to fill it in by hand.
    Use at most one of puz_file_path and puz_file_contents; leave both empty to use the library.
    """
    display_name = "Puzzle File Contents"

# Options to over/under allocate how many cross letters are in the multiworld
class LetterAllocPercent(Range):
    """
    How many letters all the Cross Letter items fill in together, as a percent of the letters
    they can reveal (see cross_letter_generation).
    100: with every Cross Letter collected, every square is filled in.
    Lower means more solving yourself; 0 makes Cross Letters do nothing. Over 100 fills the grid sooner.
    """
    display_name = "Cross Letter Allocation Percent"
    default = 100
    range_start = 0
    range_end = 9999999

# What fraction of clues to start with available
class StartingPercent(Range):
    """
    Percent of clues open at the start of the game. At least one clue is always open.
    Example: 10 on a 76-clue daily puzzle opens 8 clues.
    """
    display_name = "Starting Percent"
    default = 10
    range_start = 1 #At least one clue is required
    range_end = 100

# Option to overallocate how many clues are in the multiworld
# (This applies to non-starting clues)
class ClueAllocPercent(Range):
    """
    How many clues all the Clue Unlock items open together, as a percent of the puzzle's clues
    (the starting clues count toward it).
    100: the last clue opens with the very last Clue Unlock.
    120: built-in slack, so every clue is open a few Clue Unlocks before the last one.
    Higher means each Clue Unlock opens more clues.
    """
    display_name = "Clue Allocation Percent"
    default = 120
    range_start = 100
    range_end = 9999999


# Fraction of item rewards that should be crossword clues (vs cross letters)
class ClueItemFraction(Range):
    """
    The puzzle has one location per clue and adds the same number of items to the multiworld.
    This is the percent of those items that are Clue Unlocks; the rest are Cross Letters.
    Clue Unlocks are progression (they gate the crossword); Cross Letters are useful.
    Lower means fewer, bigger unlocks. Example: 20 on a 76-clue puzzle makes 16 Clue Unlocks
    (about 5 clues each with clue_alloc_percent 120) and 60 Cross Letters.
    """
    display_name = "Clue Item Fraction"
    default = 20
    range_start = 1
    range_end = 100


class CrossLetterGeneration(Choice):
    """
    Which letters Cross Letter items can reveal.
    in_puzzle: only squares where an across and a down clue cross.
    all: any letter of any clue.
    In American-style grids every square is crossed, so these are the same; it only matters for
    British-style grids with unchecked squares.
    """
    display_name = "Cross Letter Generation"
    option_in_puzzle = 0
    option_all = 1
    default = 0


class PuzzleSource(TextChoice):
    """
    Where the puzzle comes from when no puz_file_path or puz_file_contents is given:
    a random unplayed puzzle from the host's crossword library.
    any: any source in the library
    usa: USA Today (easier, like NYT Monday-Wednesday)
    beq: Brendan Emmett Quigley (harder, like NYT Thursday-Saturday)
    tnym: New Yorker Mini (5x5; use with puzzle_size: mini)
    Any other text picks from the library subfolder with that name.
    """
    display_name = "Puzzle Source"
    option_any = 0
    option_usa = 1
    option_beq = 2
    option_tnym = 3
    default = 0


class PuzzleSize(Choice):
    """
    Size of the library puzzle.
    mini: up to 8 squares wide (about 10 clues)
    daily: 9-17 wide, the standard 15x15 (about 75 clues)
    big: 18+ wide, Sunday-size (about 140 clues)
    any: whatever comes up
    """
    display_name = "Puzzle Size"
    option_any = 0
    option_mini = 1
    option_daily = 2
    option_big = 3
    default = 2


@dataclass
class CrosswordOptions(PerGameCommonOptions):
    # Which puzzle: a random library puzzle by source/size, unless one of the two file options is set
    puzzle_source: PuzzleSource
    puzzle_size: PuzzleSize
    puz_file_path: FilePath
    puz_file_contents: Base64FileContents

    # How many clues at game start
    starting_percent: StartingPercent
    clue_item_fraction: ClueItemFraction
    clue_alloc_percent: ClueAllocPercent
    # Cross letter items added to the multi world are just the
    # letters crossed in the original puzzle, or all letters
    # (In an American style crossword all letters are crossed anyway)
    cross_letter_generation: CrossLetterGeneration
    # Can be over 100%
    cross_letter_alloc_percent: LetterAllocPercent
