from dataclasses import dataclass
from battle_python.Battlesnake import Battlesnake
from battle_python.types import Coord


@dataclass(frozen=True)
class Board:
    height: int
    width: int
    food: list[Coord]
    hazards: list[Coord]
    snakes: list[Battlesnake]
