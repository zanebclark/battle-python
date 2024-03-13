import json
import time
from pathlib import Path

from battle_python.GameState import GameState
from battle_python.SnakeState import SnakeState
from battle_python.api_types import (
    Coord,
    SnakeDef,
    SnakeCustomizations,
)
from ..mocks.get_mock_game_state import get_mock_game_state
from ..mocks.get_mock_snake_state import get_mock_snake_state


def test_game_state_init() -> None:
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
                is_self=True,
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
    e_gs = GameState.from_payload(payload=payload)

    # Board-level assertions
    assert e_gs.board_height == mock_gs.board_height
    assert e_gs.board_width == mock_gs.board_width
    assert e_gs.current_board.food_coords == mock_gs.current_board.food_coords
    assert e_gs.current_board.hazard_coords == mock_gs.current_board.hazard_coords
    assert e_gs.current_board.turn == mock_gs.current_board.turn
    assert len(e_gs.snake_defs.keys()) == len(mock_gs.snake_defs.keys())
    assert e_gs.current_board.my_snake == mock_gs.current_board.my_snake
    assert e_gs.current_board.other_snakes == mock_gs.current_board.other_snakes
    gs_snakes = [e_gs.current_board.my_snake, *e_gs.current_board.other_snakes]
    for snake in [mock_gs.current_board.my_snake, *mock_gs.current_board.other_snakes]:
        assert e_gs.snake_defs[snake.id].name == mock_gs.snake_defs[snake.id].name
        assert (
            e_gs.snake_defs[snake.id].customizations
            == mock_gs.snake_defs[snake.id].customizations
        )
        assert e_gs.snake_defs[snake.id].is_self == mock_gs.snake_defs[snake.id].is_self

        gs_snake: SnakeState | None = None
        for index, some_snake in enumerate(gs_snakes):
            if some_snake.id == snake.id:
                gs_snake = gs_snakes.pop(index)
                break

        if not gs_snake:
            raise Exception(f"snake not found: {snake.id}")

        assert gs_snake.health == snake.health
        assert gs_snake.body == snake.body
        assert gs_snake.head == snake.head
        assert gs_snake.length == snake.length
        assert gs_snake.latency == snake.latency
        assert gs_snake.shout == snake.shout
        assert gs_snake.is_self == (snake.id == mock_gs.current_board.my_snake.id)
        assert gs_snake.murder_count == 0
        assert gs_snake.food_consumed == tuple()
        assert gs_snake.elimination is None
        assert gs_snake.prev_state is None

    # Game-level assertions
    assert e_gs.game == mock_gs.game


def test_game_state_spam() -> None:
    gs = get_mock_game_state(
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
                is_self=True,
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
    t0 = time.time()
    # prof = pprofile.Profile()
    # with prof():
    for turn in range(2):
        gs.increment_frontier(request_nanoseconds=time.time_ns() + (5000 * 1_000_000))
        t1 = time.time()
        total = t1 - t0
        print(f"turn: {turn}")
        print(f"time: {total}")
        print(f"explored_states: {len(gs.explored_states)}")
        print(f"terminal_counter: {gs.terminal_counter}")
        print(
            f"explored_states + terminal_counter: "
            f"{len(gs.explored_states) + gs.terminal_counter}"
        )
        print(f"counter: {gs.counter}")
    # prof.print_stats()
    payload = gs.current_board.get_board_payload(snake_defs=gs.snake_defs, game=gs.game)
    Path("C:\\Users\\zaneb\\GitHub_Repos\\board\\src\\move.json").write_text(
        json.dumps(payload)
    )

    # prof.print_stats()
    # TODO: If a move isn't towards me or food, drop it
    # TODO: Combine up -> right and left -> up into the same board state somehow
    # TODO: That's an interesting concept. Maybe come up with a function that would compare key attributes of the board


def test_game_state_get_next_move() -> None:
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
    gs.get_next_move(request_nanoseconds=time.time_ns())


def test_some_exception() -> None:
    payload = {
        "game": {
            "id": "aede16e0-c163-491b-8cbc-d3efa851b57c",
            "ruleset": {
                "name": "standard",
                "version": "v1.2.3",
                "settings": {
                    "foodSpawnChance": 15,
                    "minimumFood": 1,
                    "hazardDamagePerTurn": 0,
                    "hazardMap": "",
                    "hazardMapAuthor": "",
                    "royale": {"shrinkEveryNTurns": 0},
                    "squad": {
                        "allowBodyCollisions": False,
                        "sharedElimination": False,
                        "sharedHealth": False,
                        "sharedLength": False,
                    },
                },
            },
            "map": "standard",
            "timeout": 500,
            "source": "ladder",
        },
        "turn": 8,
        "board": {
            "height": 11,
            "width": 11,
            "snakes": [
                {
                    "id": "gs_vBwrGGCKvpqv7jpD9W7hTvdB",
                    "name": "devops-for-days",
                    "latency": "436",
                    "health": 94,
                    "body": [
                        {"x": 5, "y": 3},
                        {"x": 4, "y": 3},
                        {"x": 3, "y": 3},
                        {"x": 2, "y": 3},
                    ],
                    "head": {"x": 5, "y": 3},
                    "length": 4,
                    "shout": "",
                    "squad": "",
                    "customizations": {
                        "color": "#ab8b9c",
                        "head": "beluga",
                        "tail": "do-sammy",
                    },
                },
                {
                    "id": "gs_j9xbRR8q6VdVQfr7Sgj87BvS",
                    "name": "Battlesnake Go!",
                    "latency": "7",
                    "health": 92,
                    "body": [{"x": 1, "y": 9}, {"x": 1, "y": 8}, {"x": 2, "y": 8}],
                    "head": {"x": 1, "y": 9},
                    "length": 3,
                    "shout": "",
                    "squad": "",
                    "customizations": {
                        "color": "#ff00ff",
                        "head": "tiger-king",
                        "tail": "tiger-tail",
                    },
                },
                {
                    "id": "gs_WvpHJrH8yFQpryWDGxQqGckY",
                    "name": "Carl Gustav Jung",
                    "latency": "12",
                    "health": 94,
                    "body": [
                        {"x": 4, "y": 8},
                        {"x": 4, "y": 9},
                        {"x": 4, "y": 10},
                        {"x": 5, "y": 10},
                    ],
                    "head": {"x": 4, "y": 8},
                    "length": 4,
                    "shout": "",
                    "squad": "",
                    "customizations": {
                        "color": "#00ccff",
                        "head": "all-seeing",
                        "tail": "mystic-moon",
                    },
                },
                {
                    "id": "gs_38PmM8VjxkGVpTPtYgBrXP7C",
                    "name": "Maxine the Mule",
                    "latency": "500",
                    "health": 92,
                    "body": [{"x": 9, "y": 9}, {"x": 9, "y": 8}, {"x": 9, "y": 7}],
                    "head": {"x": 9, "y": 9},
                    "length": 3,
                    "shout": "",
                    "squad": "",
                    "customizations": {
                        "color": "#ff5500",
                        "head": "ghost",
                        "tail": "leaf",
                    },
                },
            ],
            "food": [{"x": 0, "y": 8}, {"x": 8, "y": 0}, {"x": 5, "y": 5}],
            "hazards": [],
        },
        "you": {
            "id": "gs_vBwrGGCKvpqv7jpD9W7hTvdB",
            "name": "devops-for-days",
            "latency": "436",
            "health": 94,
            "body": [
                {"x": 5, "y": 3},
                {"x": 4, "y": 3},
                {"x": 3, "y": 3},
                {"x": 2, "y": 3},
            ],
            "head": {"x": 5, "y": 3},
            "length": 4,
            "shout": "",
            "squad": "",
            "customizations": {
                "color": "#ab8b9c",
                "head": "beluga",
                "tail": "do-sammy",
            },
        },
    }
    gs = GameState.from_payload(payload=payload)
    gs.get_next_move(request_nanoseconds=time.time_ns())
    for turn in range(2):
        gs.increment_frontier(request_nanoseconds=time.time_ns() + (5000 * 1_000_000))
