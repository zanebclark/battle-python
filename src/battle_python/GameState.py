from dataclasses import dataclass
from battle_python.Board import Board
from battle_python.Battlesnake import Battlesnake

from battle_python.types import Game


@dataclass
class GameState:
    game: Game
    turn: int
    board: Board
    you: Battlesnake
