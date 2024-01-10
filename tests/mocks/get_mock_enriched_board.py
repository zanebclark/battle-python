from battle_python.EnrichedBoard import EnrichedBoard
from battle_python.SnakeState import SnakeState
from battle_python.api_types import Coord


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
