from dataclasses import dataclass

from Options import Choice, FreeText, PerGameCommonOptions, Range

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
    
    #Exactly 1 of these two
    puz_file_path: FilePath
    puz_file_contents: Base64FileContents


 