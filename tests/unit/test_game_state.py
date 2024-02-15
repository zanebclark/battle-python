import json
import time
import uuid
from pathlib import Path

import boto3
import pprofile

from battle_python.BoardState import BoardState
from battle_python.GameState import GameState
from battle_python.SnakeState import SnakeState
from battle_python.api_types import (
    Coord,
    SnakeRequest,
    Game,
    Ruleset,
    Board,
    SnakeCustomizations,
    SnakeDef,
)
from mocks.get_mock_game_state import get_mock_game_state
from mocks.get_mock_snake_state import get_mock_snake_state

from mocks.mock_api_types import get_mock_snake


def test_game_state_init():
    you = get_mock_snake(
        body_coords=(
            Coord(x=0, y=0),
            Coord(x=0, y=1),
            Coord(x=0, y=2),
        )
    )
    snakes = [
        you,
        get_mock_snake(
            body_coords=(
                Coord(x=10, y=0),
                Coord(x=10, y=1),
                Coord(x=10, y=2),
            )
        ),
    ]

    game = Game(
        id=str(uuid.uuid4()),
        ruleset=Ruleset(
            name="standard",
            version=str(uuid.uuid4()),
            settings={
                "foodSpawnChance": 10,
                "minimumFood": 11,
                "hazardDamagePerTurn": 12,
            },
        ),
        map=str(uuid.uuid4()),
        timeout=123,
        source="league",
    )

    board = Board(
        height=11,
        width=12,
        food=(
            Coord(x=1, y=1),
            Coord(x=10, y=10),
        ),
        hazards=(
            Coord(x=10, y=1),
            Coord(x=2, y=10),
        ),
        snakes=snakes,
    )

    gs = SnakeRequest(
        game=game,
        turn=12,
        board=board,
        you=you,
    )

    e_gs = GameState.from_payload(payload=gs.model_dump())

    # Board-level assertions
    assert e_gs.board_height == board.height
    assert e_gs.board_width == board.width
    assert e_gs.current_board.food_coords == board.food
    assert e_gs.current_board.hazard_coords == board.hazards
    assert e_gs.current_board.turn == gs.turn
    assert len(e_gs.snake_defs.keys()) == len(snakes)
    gs_snakes = [e_gs.current_board.my_snake, *e_gs.current_board.other_snakes]
    for snake in snakes:
        assert e_gs.snake_defs[snake.id].name == snake.name
        assert e_gs.snake_defs[snake.id].customizations == snake.customizations
        assert e_gs.snake_defs[snake.id].is_self == (snake.id == you.id)

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
        assert gs_snake.latency == int(snake.latency)
        assert gs_snake.shout == snake.shout
        assert gs_snake.is_self == (snake.id == you.id)
        assert gs_snake.murder_count == 0
        assert gs_snake.food_consumed == tuple()
        assert gs_snake.elimination is None
        assert gs_snake.prev_state is None

    # Game-level assertions
    assert e_gs.game == gs.game


# def test_game_state_spam():
#     gs = get_mock_game_state(
#         board_height=11,
#         board_width=11,
#         food_coords=(Coord(x=3, y=9),),
#         snakes={
#             SnakeDef(
#                 id="Up -> Right",
#                 name="Up -> Right",
#                 customizations=SnakeCustomizations(head="all-seeing"),
#             ): get_mock_snake_state(
#                 snake_id="Up -> Right",
#                 body_coords=(
#                     Coord(x=0, y=10),
#                     Coord(x=0, y=9),
#                     Coord(x=0, y=8),
#                 ),
#                 murder_count=0,
#                 health=89,
#             ),
#             SnakeDef(
#                 id="Sidecar",
#                 name="Sidecar",
#                 customizations=SnakeCustomizations(
#                     head="caffeine", tail="coffee", color="#9ffcc9"
#                 ),
#             ): get_mock_snake_state(
#                 snake_id="Sidecar",
#                 body_coords=(
#                     Coord(x=1, y=9),
#                     Coord(x=1, y=8),
#                     Coord(x=1, y=7),
#                 ),
#                 murder_count=0,
#                 health=64,
#             ),
#             SnakeDef(
#                 id="SecondSidecar",
#                 name="SecondSidecar",
#                 customizations=SnakeCustomizations(
#                     head="beluga", tail="do-sammy", color="#ab8b9c"
#                 ),
#             ): get_mock_snake_state(
#                 is_self=True,
#                 snake_id="SecondSidecar",
#                 body_coords=(
#                     Coord(x=2, y=10),
#                     Coord(x=2, y=9),
#                     Coord(x=2, y=8),
#                 ),
#                 murder_count=0,
#                 health=64,
#             ),
#             SnakeDef(
#                 id="Rando",
#                 name="Rando",
#                 customizations=SnakeCustomizations(
#                     head="bendr", tail="curled", color="#714bb5"
#                 ),
#             ): get_mock_snake_state(
#                 snake_id="Rando",
#                 body_coords=(
#                     Coord(x=8, y=1),
#                     Coord(x=9, y=1),
#                     Coord(x=10, y=1),
#                 ),
#                 murder_count=0,
#                 health=64,
#             ),
#         },
#         my_snake_id="SecondSidecar",
#     )
#     t0 = time.time()
#     # prof = pprofile.Profile()
#     # with prof():
#     for turn in range(8):
#         gs.increment_frontier()
#         t1 = time.time()
#         total = t1 - t0
#         print(f"turn: {turn}")
#         print(f"time: {total}")
#         print(f"explored_states: {len(gs.explored_states)}")
#         print(f"terminal_counter: {gs.terminal_counter}")
#         print(
#             f"explored_states + terminal_counter: "
#             f"{len(gs.explored_states) + gs.terminal_counter}"
#         )
#         print(f"counter: {gs.counter}")
#     # prof.print_stats()
#     payload = gs.current_board.get_board_payload(snake_defs=gs.snake_defs, game=gs.game)
#     Path("C:\\Users\\zaneb\\GitHub_Repos\\board\\src\\move.json").write_text(
#         json.dumps(payload)
#     )
#
#     # prof.print_stats()
#     # TODO: If a move isn't towards me or food, drop it
#     # TODO: Combine up -> right and left -> up into the same board state somehow
#     # TODO: That's an interesting concept. Maybe come up with a function that would compare key attributes of the board
def test_game_state_spam():
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
        my_snake_id="C",
    )
    t0 = time.time()
    # prof = pprofile.Profile()
    # with prof():
    for turn in range(5):
        gs.increment_frontier()
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


def test_spam():
    example_move = Path(__file__).parent.parent / "assets" / "move.json"
    json_string = example_move.read_text()
    move = json.loads(json_string)

    dyn_resource = boto3.resource("dynamodb")
    table = dyn_resource.Table("ATestTable")
    # table.load()
    print("hey there!")
    t0 = time.time()
    table.put_item(
        Item={
            "GameId": "abcdefg",
            "Turn": 123,
            "something": "something",
        }
    )
    item = table.get_item(Key={"GameId": move["game"]["id"], "Turn": int(move["turn"])})
    t1 = time.time()
    total = t1 - t0
    print(f"total: {total}")
