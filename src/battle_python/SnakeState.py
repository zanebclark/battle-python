from __future__ import annotations

import structlog
from typing import Literal, Any
from pydantic import NonNegativeInt, Field, BaseModel

from battle_python.api_types import Coord, CoordAsDict

logger = structlog.get_logger()


class Elimination(BaseModel):
    cause: Literal[
        "snake-collision",
        "snake-self-collision",
        "out-of-health",
        "hazard",
        "head-collision",
        "wall-collision",
        "unknown",
    ]
    by: str | None = None


class SnakeState(BaseModel):
    id: str
    health: NonNegativeInt
    body: tuple[CoordAsDict, ...]
    head: CoordAsDict
    length: NonNegativeInt
    latency: str
    shout: str | None = None
    is_self: bool = False
    murder_count: int = 0
    food_consumed: tuple[CoordAsDict, ...] = Field(default_factory=tuple)
    elimination: Elimination | None = None
    prev_state: SnakeState | None = Field(default=None, exclude=True)

    @property
    def last_move(self) -> Coord:
        return Coord(
            x=(self.body[0].x - self.body[1].x), y=self.body[0].y - self.body[1].y
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SnakeState):
            return self.model_dump() == other.model_dump()
        return super().__eq__(other)
