from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Literal

Direction = Literal["up", "down", "left", "right"]

GameSource = Literal["tournament", "league", "arena", "challenge", "custom"]


@dataclass(frozen=True)
class BattlesnakeCustomizations:
    color: str | None
    head: str | None
    tail: str | None


@dataclass(frozen=True, kw_only=True)
class BattlesnakeDetails(BattlesnakeCustomizations):
    author: str | None
    version: str | None
    apiversion: Literal["1"] = "1"


@dataclass(frozen=True)
class Ruleset:
    name: str
    version: str
    settings: dict


@dataclass(frozen=True)
class Game:
    id: str
    ruleset: Ruleset
    map: str
    timeout: int
    source: GameSource


@dataclass(frozen=True)
class Coord:
    x: int
    y: int

    def get_legal_moves(self, board_width: int, board_height: int):
        moves = self.get_potential_moves()
        for coord in list(moves.keys()):
            if (
                coord.x < 0
                or coord.x > board_width - 1
                or coord.y < 0
                or coord.y > board_height - 1
            ):
                del moves[coord]
                continue

        return moves

    def get_potential_moves(self) -> dict[Coord, Direction]:
        moves: dict[Coord, Direction] = {
            Coord(self.x, self.y + 1): "up",
            Coord(self.x, self.y - 1): "down",
            Coord(self.x - 1, self.y): "left",
            Coord(self.x + 1, self.y): "right",
        }
        return moves


def get_board_coords(board_width: int, board_height: int) -> list[Coord]:
    coords: list[Coord] = [
        Coord(x=x, y=y) for x, y in product(range(board_width), range(board_height))
    ]
    return coords


@dataclass(frozen=True)
class MoveResponse:
    move: Direction
    shout: str | None = None


@dataclass
class Battlesnake:
    id: str
    name: str
    health: int
    body: list[Coord]
    latency: str
    head: Coord
    length: int
    shout: str
    customizations: BattlesnakeCustomizations
    is_self: bool = False


@dataclass(frozen=True)
class Board:
    height: int
    width: int
    food: list[Coord]
    hazards: list[Coord]
    snakes: list[Battlesnake]


@dataclass
class GameState:
    game: Game
    turn: int
    board: Board
    you: Battlesnake

    def mark_your_snake(self):
        for snake in self.board.snakes:
            if snake.id == self.you.id:
                snake.is_self = True
                continue

    def __post_init__(self):
        self.mark_your_snake()
