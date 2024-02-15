from battle_python.BoardState import BoardState
from battle_python.SnakeState import SnakeState
from battle_python.api_types import Coord


def get_mock_board_state(
    my_snake: SnakeState,
    turn: int = 0,
    board_height: int = 11,
    board_width: int = 11,
    hazard_damage_rate: int = 14,
    food_coords: tuple[Coord, ...] = tuple(),
    hazard_coords: tuple[Coord, ...] = tuple(),
    other_snakes: tuple[SnakeState, ...] = tuple(),
) -> BoardState:
    return BoardState.factory(
        turn=turn,
        board_width=board_width,
        board_height=board_height,
        food_coords=food_coords,
        hazard_coords=hazard_coords,
        my_snake=my_snake,
        other_snakes=other_snakes,
        hazard_damage_rate=hazard_damage_rate,
    )
