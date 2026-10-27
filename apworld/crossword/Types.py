from dataclasses import dataclass
from enum import Enum

class Direction(Enum):
    ACROSS = "Across"
    DOWN = "Down"


@dataclass(frozen=True)
class ClueId:
    direction: Direction
    number: int


@dataclass(frozen=True)
class ClueInfo:
    clue: str
    answer: str

@dataclass
class Clue:
    direction: Direction
    number: int
    clue: str
    answer: str

    def get_id(self):
        return ClueId(self.direction, self.number)

@dataclass(frozen=True)
class CrossLetter:
    clue_id: ClueId
    index: int
    value: str

@dataclass(frozen=True)
class ParsedPuz:
    clues: list[Clue]
    cross_letters: list[CrossLetter]

@dataclass(frozen=True)
class SlotData:
    n_starting_clues: int
    clues_per_reward: float
    cross_letters_per_reward: float
    clues: list[Clue]
    cross_letters: list[CrossLetter]