import uuid

from battle_python.api_types import Coord, SnakeCustomizations
from battle_python.game_state import (
    SnakeState,
    EnrichedBoard,
    EnrichedGameState,
    SnakeDef,
)
from mocks.mock_api_types import get_mock_standard_game


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


def get_mock_snake_def(
    snake_id: str | None = None,
    is_self: bool = False,
) -> SnakeDef:
    if snake_id is None:
        snake_id = str(uuid.uuid4())
    return SnakeDef(
        id=snake_id,
        name=f"mock_battlesnake_{snake_id}",
        customizations=SnakeCustomizations(
            color="#888888", head="all-seeing", tail="curled"
        ),
        is_self=is_self,
    )


def get_mock_enriched_board(
    turn: int = 0,
    board_height: int = 11,
    board_width: int = 11,
    food_prob: dict[Coord, float] | None = None,
    hazard_prob: dict[Coord, float] | None = None,
    snake_states: list[SnakeState] | None = None,
) -> EnrichedBoard:
    if not food_prob:
        food_prob = {}
    if not hazard_prob:
        hazard_prob = {}
    if not snake_states:
        snake_states = []

    return EnrichedBoard(
        turn=turn,
        board_width=board_width,
        board_height=board_height,
        food_prob=food_prob,
        hazard_prob=hazard_prob,
        snake_states=snake_states,
    )


def get_mock_enriched_gamestate(
    snakes: dict[SnakeDef, SnakeState],
    current_turn: int = 0,
    turns: list[EnrichedBoard] | None = None,
    # get_mock_standard_game args
    food_spawn_chance: int = 15,
    minimum_food: int = 1,
    hazard_damage_per_turn: int = 14,
    timeout: int = 500,
    # get_mock_enriched_board args
    board_height: int = 11,
    board_width: int = 11,
    food_coords: list[Coord] | None = None,
    hazard_coords: list[Coord] | None = None,
) -> EnrichedGameState:
    snake_states: list[SnakeState] = []
    snake_defs: dict[str, SnakeDef] = {}

    for snake_def, snake_state in snakes.items():
        snake_states.append(snake_state)
        snake_defs[snake_def.id] = snake_def

    game = get_mock_standard_game(
        food_spawn_chance=food_spawn_chance,
        minimum_food=minimum_food,
        hazard_damage_per_turn=hazard_damage_per_turn,
        timeout=timeout,
    )

    if not turns:
        turns = [
            get_mock_enriched_board(
                board_height=board_height,
                board_width=board_width,
                food_prob=food_coords,
                hazard_prob=hazard_coords,
                snake_states=snake_states,
            )
        ]

    return EnrichedGameState(
        game=game,
        board_height=board_height,
        board_width=board_width,
        current_turn=current_turn,
        turns=turns,
        snake_defs=snake_defs,
    )
