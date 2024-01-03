from dataclasses import dataclass
from typing import Dict, Literal, Optional, List


@dataclass(frozen=True)
class BattlesnakeCustomizations:
    color: Optional[str]
    head: Optional[str]
    tail: Optional[str]


@dataclass(frozen=True, kw_only=True)
class BattlesnakeDetails(BattlesnakeCustomizations):
    apiversion: Literal["1"] = "1"
    author: Optional[str]
    version: Optional[str]


GameSource = Literal["tournament", "league", "arena", "challenge", "custom"]


@dataclass(frozen=True)
class Ruleset:
    name: str
    version: str
    settings: Dict


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


@dataclass
class Battlesnake:
    id: str
    name: str
    health: int
    body: List[Coord]
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
    food: List[Coord]
    hazards: List[Coord]
    snakes: List[Battlesnake]


@dataclass(frozen=True)
class GameState:
    game: Game
    turn: int
    board: Board
    you: Battlesnake

    def __post_init__(self):
        for snake in self.board.snakes:
            if snake.id == self.you.id:
                snake.is_self = True
                break


MoveDirection = Literal["up", "down", "left", "right"]


@dataclass(frozen=True)
class MoveResponse:
    move: MoveDirection
    shout: Optional[str] = None
