import uuid

from battle_python.BoardState import BoardState
from battle_python.GameState import GameState
from battle_python.SnakeState import SnakeState
from battle_python.api_types import (
    Coord,
    SnakeCustomizations,
    SnakeDef,
    Game,
    Ruleset,
    RulesetSettings,
)
from .get_mock_board_state import get_mock_board_state


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


def get_mock_standard_game(
    food_spawn_chance: int = 10,
    minimum_food: int = 20,
    hazard_damage_per_turn: int = 30,
    timeout: int = 500,
) -> Game:
    return Game(
        id=str(uuid.uuid4()),
        ruleset=Ruleset(
            name="standard",
            version="v1.1.15",
            settings=RulesetSettings(
                foodSpawnChance=food_spawn_chance,
                minimumFood=minimum_food,
                hazardDamagePerTurn=hazard_damage_per_turn,
            ),
        ),
        map="standard",
        source="custom",
        timeout=timeout,
    )


def get_mock_game_state(
    snakes: dict[SnakeDef, SnakeState],
    current_board: BoardState | None = None,
    # get_mock_standard_game args
    food_spawn_chance: int = 15,
    minimum_food: int = 1,
    hazard_damage_per_turn: int = 14,
    timeout: int = 500,
    # get_mock_enriched_board args
    board_height: int = 11,
    board_width: int = 11,
    food_coords: tuple[Coord, ...] = tuple(),
    hazard_coords: tuple[Coord, ...] = tuple(),
) -> GameState:
    snake_defs: dict[str, SnakeDef] = {
        snake_def.id: snake_def for snake_def in snakes.keys()
    }
    my_snakes = [snake for snake in snakes.values() if snake.is_self]
    if len(my_snakes) == 0:
        raise Exception("Your snake is not defined")
    elif len(my_snakes) > 1:
        raise Exception("Your snake is defined multiple times")
    my_snake = my_snakes[0]

    game = get_mock_standard_game(
        food_spawn_chance=food_spawn_chance,
        minimum_food=minimum_food,
        hazard_damage_per_turn=hazard_damage_per_turn,
        timeout=timeout,
    )

    if not current_board:
        current_board = get_mock_board_state(
            board_height=board_height,
            board_width=board_width,
            food_coords=food_coords,
            hazard_coords=hazard_coords,
            other_snakes=tuple(
                (snake for snake in snakes.values() if not snake.is_self)
            ),
            my_snake=my_snake,
            hazard_damage_rate=hazard_damage_per_turn,
        )

    return GameState(
        game=game,
        board_height=board_height,
        board_width=board_width,
        current_board=current_board,
        snake_defs=snake_defs,
    )
