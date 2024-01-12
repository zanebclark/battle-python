from __future__ import annotations

from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import NonNegativeInt, Field
from battle_python.api_types import Coord


class SnakeState(BaseModel):
    snake_id: str
    health: NonNegativeInt
    body: list[Coord]
    head: Coord
    length: NonNegativeInt
    latency: NonNegativeInt
    shout: str | None = None
    is_self: bool = False
    murder_count: int = 0
    food_consumed: list[Coord] = Field(default_factory=list)
    is_eliminated: bool = False
    prev_state: SnakeState | None = None
