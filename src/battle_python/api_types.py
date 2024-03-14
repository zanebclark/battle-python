from __future__ import annotations

from typing import Literal, NamedTuple
from pydantic import NonNegativeInt, ConfigDict, BaseModel

Direction = Literal[
    "up",
    "down",
    "left",
    "right",
]

GameSource = Literal["tournament", "league", "arena", "challenge", "custom", "ladder"]

RulesetName = Literal[
    "constrictor",
    "royale",
    "solo",
    "standard",
    "wrapped",
    "wrapped_constrictor",
]


class FrozenBaseModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class SnakeCustomizations(FrozenBaseModel):
    color: str = "#888888"
    head: str = "default"
    tail: str = "default"


class SnakeMetadataResponse(SnakeCustomizations):
    author: str | None = None
    version: str | None = None
    apiversion: Literal["1"] = "1"


class SnakeDef(FrozenBaseModel):
    id: str
    name: str
    customizations: SnakeCustomizations
    is_self: bool = False


class RoyaleSettings(FrozenBaseModel):
    shrinkEveryNTurns: int


class RulesetSettings(FrozenBaseModel):
    foodSpawnChance: int
    minimumFood: int
    hazardDamagePerTurn: int
    royale: RoyaleSettings | None = None


class Ruleset(FrozenBaseModel):
    name: RulesetName
    version: str
    settings: RulesetSettings


class Game(FrozenBaseModel):
    id: str
    ruleset: Ruleset
    map: str
    timeout: NonNegativeInt
    source: GameSource


class Coord(NamedTuple):
    x: int
    y: int

    def __repr__(self) -> str:
        return f"<Coord {self.x}, {self.y}>"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def get_adjacent(self) -> set[Coord]:
        return {
            Coord(x=self.x, y=self.y + 1),
            Coord(x=self.x, y=self.y - 1),
            Coord(x=self.x - 1, y=self.y),
            Coord(x=self.x + 1, y=self.y),
        }

    def get_relative_distance(self, other: Coord) -> int:
        return abs(self.x - other.x) ** 2 + abs(self.y - other.y) ** 2

    def get_manhattan_distance(self, other: Coord) -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __lt__(self, other: Coord) -> bool:  # type: ignore
        return f"{self.x}, {self.y}" < f"{other.x}, {other.y}"

    def __le__(self, other: Coord) -> bool:  # type: ignore
        return f"{self.x}, {self.y}" <= f"{other.x}, {other.y}"

    def __gt__(self, other: Coord) -> bool:  # type: ignore
        return f"{self.x}, {self.y}" > f"{other.x}, {other.y}"

    def __ge__(self, other: Coord) -> bool:  # type: ignore
        return f"{self.x}, {self.y}" >= f"{other.x}, {other.y}"

    def __add__(self, other: Coord) -> Coord:  # type: ignore
        return Coord(x=self.x + other.x, y=self.y + other.y)

    @property
    def as_dict(self) -> dict:
        return {"x": self.x, "y": self.y}


class MoveResponse(FrozenBaseModel):
    move: Direction
    shout: str | None = None


class Snake(BaseModel):
    id: str
    name: str
    health: NonNegativeInt
    body: tuple[Coord, ...]
    latency: str
    head: Coord
    length: NonNegativeInt
    shout: str | None
    customizations: SnakeCustomizations


class Board(FrozenBaseModel):
    height: NonNegativeInt
    width: NonNegativeInt
    food: tuple[Coord, ...]
    hazards: tuple[Coord, ...]
    snakes: tuple[Snake, ...]


class SnakeRequest(BaseModel):
    game: Game
    turn: NonNegativeInt
    board: Board
    you: Snake

    @property
    def snake_game_id(self) -> str:
        return f"{self.you.id}__{self.game.id}"
