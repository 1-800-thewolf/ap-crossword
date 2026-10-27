import typing

from BaseClasses import Location
from worlds.crossword.Types import Direction

class CrosswordLocation(Location):
    game: str = "Crossword"

    def __init__(self, player: int, name: str, address: typing.Optional[int], parent):
        super().__init__(player, name, address, parent)

MAX_N_CLUES = 1000
LOCATION_OFFSET = MAX_N_CLUES * 10;



def get_location_name(clue_id: int, direction: Direction):
    return f"Solved Clue {clue_id} {direction.value}"

def get_location_id(clue_id: int, direction: Direction):
    return clue_id + (LOCATION_OFFSET if direction == Direction.DOWN else 0);

location_table = {
    get_location_name(i, dir): get_location_id(i, dir) 
    for dir in [Direction.ACROSS, Direction.DOWN] 
    for i in range(0, MAX_N_CLUES)
    } | {"VictoryLocation": LOCATION_OFFSET * 2}