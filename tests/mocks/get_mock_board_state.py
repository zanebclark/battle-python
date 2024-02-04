from battle_python.BoardState import BoardState
from battle_python.SnakeState import SnakeState
from battle_python.api_types import Coord


def get_mock_board_state(
    turn: int = 0,
    board_height: int = 11,
    board_width: int = 11,
    hazard_damage_rate: int = 14,
    food_coords: tuple[Coord, ...] | None = None,
    hazard_coords: tuple[Coord, ...] | None = None,
    snake_states: tuple[SnakeState, ...] | None = None,
    my_snake_state: SnakeState | None = None,
) -> BoardState:
    if not food_coords:
        food_coords = tuple()
    if not hazard_coords:
        hazard_coords = tuple()
    if not snake_states:
        snake_states = tuple()
    if not my_snake_state:
        if not snake_states:
            raise Exception("No snakes defined")
        my_snake_state = snake_states[0]

    return BoardState(
        turn=turn,
        board_width=board_width,
        board_height=board_height,
        food_coords=food_coords,
        hazard_coords=hazard_coords,
        snake_states=snake_states,
        hazard_damage_rate=hazard_damage_rate,
        my_snake_state=my_snake_state,
    )
