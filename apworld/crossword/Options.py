from dataclasses import dataclass

from Options import Choice, FreeText, PerGameCommonOptions, Range, TextChoice

class FilePath(FreeText):
    pass

class Base64FileContents(FreeText):
    pass

# Options to over/under allocate how many cross letters are in the multiworld
class LetterAllocPercent(Range):
    default = 100
    range_start = 0
    range_end = 9999999

# What fraction of clues to start with available
class StartingPercent(Range):
    default = 10
    range_start = 1 #At least one clue is required
    range_end = 100

# Option to overallocate how many clues are in the multiworld
# (This applies to non-starting clues)
class ClueAllocPercent(Range):
    default = 120
    range_start = 100
    range_end = 9999999


# Fraction of item rewards that should be crossword clues (vs cross letters)
class ClueItemFraction(Range):
    default = 20
    range_start = 1
    range_end = 100
    

class CrossLetterGeneration(Choice):
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
    Any other text picks from the library subfolder with that name.
    """
    display_name = "Puzzle Source"
    option_any = 0
    option_usa = 1
    option_beq = 2
    default = 0


class PuzzleSize(Choice):
    """
    Size of the library puzzle.
    mini: up to 8 squares wide; daily: 9-17 (standard 15x15); big: 18+ (Sunday-size); any: whatever comes up
    """
    display_name = "Puzzle Size"
    option_any = 0
    option_mini = 1
    option_daily = 2
    option_big = 3
    default = 2


@dataclass
class CrosswordOptions(PerGameCommonOptions):
    # Cross letter items added to the multi world are just the 
    # letters crossed in the original puzzle, or all letters
    # (In an American style crossword all letters are crossed anyway)
    cross_letter_generation: CrossLetterGeneration
    # Can be over 100%
    cross_letter_alloc_percent: LetterAllocPercent
    # How many clues at game start
    starting_percent: StartingPercent
    clue_alloc_percent: ClueAllocPercent
    clue_item_fraction: ClueItemFraction
    
    #At most 1 of these two; with neither, a library puzzle is picked by puzzle_source/puzzle_size
    puz_file_path: FilePath
    puz_file_contents: Base64FileContents
    puzzle_source: PuzzleSource
    puzzle_size: PuzzleSize


 