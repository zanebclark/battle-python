from __future__ import annotations

from typing import Literal
from aws_lambda_powertools.utilities.parser import BaseModel

Direction = Literal["up", "down", "left", "right"]

GameSource = Literal["tournament", "league", "arena", "challenge", "custom"]


class BattlesnakeCustomizations(BaseModel):
    color: str | None
    head: str | None
    tail: str | None


class BattlesnakeDetails(BattlesnakeCustomizations):
    author: str | None
    version: str | None
    apiversion: Literal["1"] = "1"


class Ruleset(BaseModel):
    name: str
    version: str
    settings: dict


class Game(BaseModel):
    id: str
    ruleset: Ruleset
    map: str
    timeout: int
    source: GameSource


class Coord(BaseModel):
    x: int
    y: int


class MoveResponse(BaseModel):
    move: Direction
    shout: str | None = None


class Battlesnake(BaseModel):
    id: str
    name: str
    health: int
    body: list[Coord]
    latency: str
    head: Coord
    length: int
    shout: str
    customizations: BattlesnakeCustomizations


class Board(BaseModel):
    height: int
    width: int
    food: list[Coord]
    hazards: list[Coord]
    snakes: list[Battlesnake]


class GameState(BaseModel):
    game: Game
    turn: int
    board: Board
    you: Battlesnake
