import uuid

import numpy as np
import numpy.typing as npt

from battle_python.BoardState import BoardState
from battle_python.SnakeState import SnakeState, Elimination
from battle_python.api_types import Coord
from battle_python.constants import DEATH_COORD


def get_mock_snake_state(
    body_coords: tuple[Coord, ...],
    board_array: npt.NDArray[np.int_] | None = None,
    snake_id: str | None = None,
    health: int = 60,
    latency: int | None = 456,
    shout: str | None = None,
    is_self: bool = False,
    murder_count: int = 0,
    food_consumed: tuple[Coord, ...] = tuple(),
    elimination: Elimination | None = None,
    prev_state: SnakeState | None = None,
) -> SnakeState:
    if not all(
        [
            abs((a_coord.x - b_coord.x) + (a_coord.y - b_coord.y)) <= 1
            for a_coord, b_coord in zip(body_coords[:-1], body_coords[1:])
        ]
    ):
        raise Exception(f"body_coords aren't contiguous: {body_coords}")

    if snake_id is None:
        snake_id = str(uuid.uuid4())
    if len(body_coords) == 1 and body_coords[0] == DEATH_COORD:
        elimination = Elimination(cause="wall-collision")
    return SnakeState(
        id=snake_id,
        health=health,
        body=body_coords,
        head=body_coords[0],
        length=len(body_coords),
        latency=str(latency),
        shout=shout,
        is_self=is_self,
        murder_count=murder_count,
        food_consumed=food_consumed,
        elimination=elimination,
        prev_state=prev_state,
    )
