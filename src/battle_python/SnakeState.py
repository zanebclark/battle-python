from __future__ import annotations

from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import NonNegativeInt, Field
from battle_python.api_types import Coord


class SnakeState(BaseModel):
    snake_id: str
    health: NonNegativeInt
    body: tuple[Coord, ...]
    head: Coord
    length: NonNegativeInt
    latency: NonNegativeInt
    shout: str | None = None
    is_self: bool = False
    murder_count: int = 0
    food_consumed: tuple[Coord, ...] = Field(default_factory=tuple)
    is_eliminated: bool = False
    prev_state: SnakeState | None = None

    @property
    def last_move(self):
        return Coord(
            x=(self.body[0].x - self.body[1].x), y=self.body[0].y - self.body[1].y
        )
