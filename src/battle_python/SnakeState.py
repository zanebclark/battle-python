from __future__ import annotations

from typing import Literal, Any
from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import NonNegativeInt, Field, ConfigDict

from battle_python.api_types import Coord
from aws_lambda_powertools import Logger

logger = Logger()


class Elimination(BaseModel):
    cause: Literal[
        "snake-collision",
        "snake-self-collision",
        "out-of-health",
        "hazard",
        "head-collision",
        "wall-collision",
    ]
    by: str | None = None


class SnakeState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str
    health: NonNegativeInt
    body: tuple[Coord, ...]
    head: Coord
    length: NonNegativeInt
    latency: NonNegativeInt
    shout: str | None = None
    is_self: bool = False
    murder_count: int = 0
    food_consumed: tuple[Coord, ...] = Field(default_factory=tuple)
    elimination: Elimination | None = None
    prev_state: SnakeState | None = Field(default=None, exclude=True)

    @property
    def last_move(self):
        return Coord(
            x=(self.body[0].x - self.body[1].x), y=self.body[0].y - self.body[1].y
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SnakeState):
            return self.model_dump() == other.model_dump()
        return super().__eq__(other)
