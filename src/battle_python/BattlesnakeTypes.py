from dataclasses import dataclass
from typing import Dict, Literal, Optional, List


@dataclass
class BattlesnakeCustomizations:
    color: Optional[str]
    head: Optional[str]
    tail: Optional[str]


@dataclass(kw_only=True)
class BattlesnakeDetails(BattlesnakeCustomizations):
    apiversion: Literal["1"] = "1"
    author: Optional[str]
    version: Optional[str]


GameSource = Literal["tournament", "league", "arena", "challenge", "custom"]


@dataclass
class Ruleset:
    name: str
    version: str
    settings: Dict


@dataclass
class Game:
    id: str
    ruleset: Ruleset
    map: str
    timeout: int
    source: GameSource


@dataclass
class Coordinate:
    x: int
    y: int


@dataclass
class Battlesnake:
    id: str
    name: str
    health: int
    body: List[Coordinate]
    latency: str
    head: Coordinate
    length: int
    shout: str
    customizations: BattlesnakeCustomizations


@dataclass
class Board:
    height: int
    width: int
    food: List[Coordinate]
    hazards: List[Coordinate]
    snakes: List[Battlesnake]


@dataclass
class GameState:
    game: Game
    turn: int
    board: Board
    you: Battlesnake


@dataclass(kw_only=True)
class GameStarted(GameState):
    turn: int = 0


@dataclass
class MoveResponse:
    move: Literal["up", "down", "left", "right"]
    shout: Optional[str] = None
