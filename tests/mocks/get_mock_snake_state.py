import uuid

from battle_python.SnakeState import SnakeState
from battle_python.api_types import Coord


def get_mock_snake_state(
    body_coords: list[Coord],
    state_prob: float = 1,
    death_prob: float = 0,
    food_prob: float = 0,
    murder_prob: float = 0,
    snake_id: str | None = None,
    health: int = 60,
    latency: int | None = 456,
    shout: str | None = None,
    is_self: bool = False,
) -> SnakeState:
    if snake_id is None:
        snake_id = str(uuid.uuid4())
    return SnakeState(
        snake_id=snake_id,
        state_prob=state_prob,
        death_prob=death_prob,
        food_prob=food_prob,
        murder_prob=murder_prob,
        health=health,
        body=body_coords,
        latency=str(latency),
        head=body_coords[0],
        length=len(body_coords),
        shout=shout,
        is_self=is_self,
    )
