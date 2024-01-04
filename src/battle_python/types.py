from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Literal

MoveDirection = Literal["up", "down", "left", "right"]

GameSource = Literal["tournament", "league", "arena", "challenge", "custom"]


@dataclass(frozen=True)
class BattlesnakeCustomizations:
    color: str | None
    head: str | None
    tail: str | None


@dataclass(frozen=True, kw_only=True)
class BattlesnakeDetails(BattlesnakeCustomizations):
    apiversion: Literal["1"] = "1"
    author: str | None
    version: str | None


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


def get_board_coords(board_width: int, board_height: int) -> list[Coord]:
    coords: list[Coord] = [
        Coord(x=x, y=y) for x, y in product(range(board_width), range(board_height))
    ]
    return coords


@dataclass(frozen=True)
class MoveResponse:
    move: MoveDirection
    shout: str | None = None
