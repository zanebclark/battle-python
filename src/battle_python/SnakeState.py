from __future__ import annotations
from typing import TYPE_CHECKING

from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import NonNegativeInt, Field

if TYPE_CHECKING:
    from battle_python.BoardState import BoardState
from battle_python.api_types import Coord


# TODO: If a snake is going to die on a turn, how do you ensure that the snake isn't considered an obstacle to future snake moves?


class SnakeState(BaseModel):
    snake_id: str
    state_prob: float
    death_prob: float
    food_prob: float
    murder_prob: float
    health: NonNegativeInt
    body: list[Coord]
    head: Coord
    length: NonNegativeInt
    latency: NonNegativeInt | None = None
    shout: str | None = None
    is_self: bool = False
    prev_state: SnakeState | None = None
