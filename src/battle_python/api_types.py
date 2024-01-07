from __future__ import annotations

from typing import Literal
from aws_lambda_powertools.utilities.parser import BaseModel, Field
from pydantic import NonNegativeInt, ConfigDict

Direction = Literal["up", "down", "left", "right"]

GameSource = Literal["tournament", "league", "arena", "challenge", "custom"]


class FrozenBaseModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class SnakeCustomizations(FrozenBaseModel):
    color: str | None
    head: str | None
    tail: str | None


class SnakeDetails(SnakeCustomizations):
    author: str | None
    version: str | None
    apiversion: Literal["1"] = "1"


class Ruleset(FrozenBaseModel):
    name: str
    version: str
    settings: dict


class Game(FrozenBaseModel):
    id: str
    ruleset: Ruleset
    map: str
    timeout: NonNegativeInt
    source: GameSource


class Coord(FrozenBaseModel):
    x: int
    y: int

    def get_adjacent(self) -> list[Coord]:
        return [
            Coord(x=self.x, y=self.y + 1),
            Coord(x=self.x, y=self.y - 1),
            Coord(x=self.x - 1, y=self.y),
            Coord(x=self.x + 1, y=self.y),
        ]


class MoveResponse(FrozenBaseModel):
    move: Direction
    shout: str | None = None


class Snake(BaseModel):
    id: str
    name: str
    health: NonNegativeInt
    body: list[Coord]
    latency: str
    head: Coord
    length: NonNegativeInt
    shout: str
    customizations: SnakeCustomizations


class Board(FrozenBaseModel):
    height: NonNegativeInt
    width: NonNegativeInt
    food: list[Coord]
    hazards: list[Coord]
    snakes: list[Snake]


class GameState(BaseModel):
    game: Game
    turn: NonNegativeInt
    board: Board
    you: Snake
