import time

import cProfile
from battle_python.GameState import GameState
from battle_python.api_types import (
    Coord,
    SnakeDef,
    SnakeCustomizations,
)
from mocks.get_mock_game_state import get_mock_game_state
from mocks.get_mock_snake_state import get_mock_snake_state


if __name__ == "__main__":
    with cProfile.Profile() as pr:
        request_time = time.time_ns() // 1_000_000
        mock_gs = get_mock_game_state(
            board_height=11,
            board_width=11,
            food_coords=(
                Coord(x=0, y=2),
                Coord(x=2, y=10),
                Coord(x=8, y=0),
                Coord(x=5, y=5),
                Coord(x=10, y=8),
            ),
            snakes={
                SnakeDef(
                    id="A",
                    name="A",
                    customizations=SnakeCustomizations(head="all-seeing"),
                ): get_mock_snake_state(
                    snake_id="A",
                    body_coords=(Coord(x=1, y=1), Coord(x=1, y=1), Coord(x=1, y=1)),
                    health=100,
                ),
                SnakeDef(
                    id="B",
                    name="B",
                    customizations=SnakeCustomizations(
                        head="caffeine", tail="coffee", color="#9ffcc9"
                    ),
                ): get_mock_snake_state(
                    snake_id="B",
                    is_self=True,
                    body_coords=(Coord(x=9, y=1), Coord(x=9, y=1), Coord(x=9, y=1)),
                    health=100,
                ),
                SnakeDef(
                    id="C",
                    name="C",
                    customizations=SnakeCustomizations(
                        head="beluga", tail="do-sammy", color="#ab8b9c"
                    ),
                ): get_mock_snake_state(
                    snake_id="C",
                    body_coords=(Coord(x=9, y=9), Coord(x=9, y=9), Coord(x=9, y=9)),
                    health=100,
                ),
                SnakeDef(
                    id="D",
                    name="D",
                    customizations=SnakeCustomizations(
                        head="bendr", tail="curled", color="#714bb5"
                    ),
                ): get_mock_snake_state(
                    snake_id="D",
                    body_coords=(Coord(x=1, y=9), Coord(x=1, y=9), Coord(x=1, y=9)),
                    health=100,
                ),
            },
        )
        payload = mock_gs.current_board.get_move_request(
            snake_defs=mock_gs.snake_defs, game=mock_gs.game
        )
        gs = GameState.from_payload(payload=payload)
        move = gs.get_next_move(request_time=request_time)
        print(gs.counter)
        print(move)
        pr.dump_stats("spam.pstat")
