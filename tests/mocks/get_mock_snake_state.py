import uuid

from battle_python.SnakeState import SnakeState
from battle_python.api_types import Coord


def get_mock_snake_state(
    body_coords: tuple[Coord, ...],
    snake_id: str | None = None,
    health: int = 60,
    latency: int | None = 456,
    shout: str | None = None,
    is_self: bool = False,
    murder_count: int = 0,
    food_consumed: tuple[Coord, ...] = tuple(),
    is_eliminated: bool = False,
    prev_state: SnakeState | None = None,
) -> SnakeState:
    if snake_id is None:
        snake_id = str(uuid.uuid4())
    return SnakeState(
        snake_id=snake_id,
        health=health,
        body=body_coords,
        head=body_coords[0],
        length=len(body_coords),
        latency=str(latency),
        shout=shout,
        is_self=is_self,
        murder_count=murder_count,
        food_consumed=food_consumed,
        is_eliminated=is_eliminated,
        prev_state=prev_state,
    )
