import uuid

import pytest

from battle_python.api_types import (
    Coord,
    GameState,
    Game,
    Ruleset,
    Board,
)
from battle_python.game_state import (
    SnakeState,
    EnrichedGameState,
    get_legal_adjacent_coords,
)
from mocks.mock_api_types import get_mock_snake
from mocks.mock_game_state import get_mock_snake_state


@pytest.mark.parametrize(
    "coord, expected",
    [
        # Left Border
        (Coord(x=0, y=10), [Coord(x=1, y=10), Coord(x=0, y=9)]),
        (Coord(x=0, y=0), [Coord(x=1, y=0), Coord(x=0, y=1)]),
        # Right Border
        (Coord(x=10, y=10), [Coord(x=9, y=10), Coord(x=10, y=9)]),
        (Coord(x=10, y=0), [Coord(x=9, y=0), Coord(x=10, y=1)]),
        # Bottom Border
        (Coord(x=0, y=0), [Coord(x=0, y=1), Coord(x=1, y=0)]),
        (Coord(x=10, y=0), [Coord(x=10, y=1), Coord(x=9, y=0)]),
        # Top Border
        (Coord(x=0, y=10), [Coord(x=0, y=9), Coord(x=1, y=10)]),
        (Coord(x=10, y=10), [Coord(x=10, y=9), Coord(x=9, y=10)]),
        # Two Options
        (Coord(x=1, y=10), [Coord(x=0, y=10), Coord(x=1, y=9), Coord(x=2, y=10)]),
        # Three Options
        (
            Coord(x=1, y=9),
            [Coord(x=1, y=10), Coord(x=0, y=9), Coord(x=1, y=8), Coord(x=2, y=9)],
        ),
    ],
)
def test_get_legal_adjacent_coords(coord: Coord, expected: list[Coord]):
    legal_adjacent_coords = get_legal_adjacent_coords(
        coord=coord,
        board_height=11,
        board_width=11,
    )
    assert sorted(legal_adjacent_coords) == sorted(expected)


@pytest.mark.parametrize(
    "snake, expected",
    [
        (
            get_mock_snake_state(
                [
                    Coord(x=0, y=2),
                    Coord(x=0, y=1),
                    Coord(x=0, y=0),
                    Coord(x=0, y=0),
                ],
            ),
            True,
        ),
        (
            get_mock_snake_state(
                [
                    Coord(x=0, y=2),
                    Coord(x=0, y=1),
                    Coord(x=0, y=0),
                ],
            ),
            False,
        ),
    ],
)
def test_snake_state_is_growing(snake: SnakeState, expected: bool):
    assert snake.is_growing() is expected


@pytest.mark.parametrize(
    "snake, coord, expected",
    [
        (
            get_mock_snake_state(
                [
                    Coord(x=0, y=2),
                    Coord(x=0, y=1),
                    Coord(x=0, y=0),
                    Coord(x=0, y=0),
                ],
            ),
            Coord(x=0, y=0),
            True,
        ),
        (
            get_mock_snake_state(
                [
                    Coord(x=0, y=2),
                    Coord(x=0, y=1),
                    Coord(x=0, y=0),
                ],
            ),
            Coord(x=0, y=0),
            False,
        ),
        (
            get_mock_snake_state(
                [
                    Coord(x=0, y=2),
                    Coord(x=0, y=1),
                    Coord(x=0, y=0),
                ],
            ),
            Coord(x=0, y=2),
            True,
        ),
    ],
)
def test_snake_state_is_collision(snake: SnakeState, coord: Coord, expected: bool):
    assert snake.is_collision(coord) is expected


@pytest.mark.parametrize(
    "snake, expected",
    [
        (  # Left Border: Up -> Right
            get_mock_snake_state(
                body_coords=[
                    Coord(x=0, y=10),
                    Coord(x=0, y=9),
                    Coord(x=0, y=8),
                ]
            ),
            [Coord(x=1, y=10)],
        ),
        (  # Left Border: Down -> Right
            get_mock_snake_state(
                body_coords=[
                    Coord(x=0, y=0),
                    Coord(x=0, y=1),
                    Coord(x=0, y=2),
                ]
            ),
            [Coord(x=1, y=0)],
        ),
        (  # Right Border: Up -> Left
            get_mock_snake_state(
                body_coords=[
                    Coord(x=10, y=10),
                    Coord(x=10, y=9),
                    Coord(x=10, y=8),
                ]
            ),
            [Coord(x=9, y=10)],
        ),
        (  # Right Border: Down -> Left
            get_mock_snake_state(
                body_coords=[
                    Coord(x=10, y=0),
                    Coord(x=10, y=1),
                    Coord(x=10, y=2),
                ]
            ),
            [Coord(x=9, y=0)],
        ),
        (  # Bottom Border: Left -> Up
            get_mock_snake_state(
                body_coords=[
                    Coord(x=0, y=0),
                    Coord(x=1, y=0),
                    Coord(x=2, y=0),
                ]
            ),
            [Coord(x=0, y=1)],
        ),
        (  # Bottom Border: Right -> Up
            get_mock_snake_state(
                body_coords=[
                    Coord(x=10, y=0),
                    Coord(x=9, y=0),
                    Coord(x=8, y=0),
                ]
            ),
            [Coord(x=10, y=1)],
        ),
        (  # Top Border: Left -> Down
            get_mock_snake_state(
                body_coords=[
                    Coord(x=0, y=10),
                    Coord(x=1, y=10),
                    Coord(x=2, y=10),
                ]
            ),
            [Coord(x=0, y=9)],
        ),
        (  # TopBorder:  Right -> Down
            get_mock_snake_state(
                body_coords=[
                    Coord(x=10, y=10),
                    Coord(x=9, y=10),
                    Coord(x=8, y=10),
                ]
            ),
            [Coord(x=10, y=9)],
        ),
        # Two Options
        (
            get_mock_snake_state(
                body_coords=[
                    Coord(x=1, y=10),
                    Coord(x=2, y=10),
                    Coord(x=3, y=10),
                ]
            ),
            [
                Coord(x=0, y=10),
                Coord(x=1, y=9),
            ],
        ),
        # Three Options
        (
            get_mock_snake_state(
                body_coords=[
                    Coord(x=1, y=9),
                    Coord(x=2, y=9),
                    Coord(x=3, y=9),
                ]
            ),
            [
                Coord(x=1, y=10),
                Coord(x=0, y=9),
                Coord(x=1, y=8),
            ],
        ),
        # Ouroboros
        (
            get_mock_snake_state(
                body_coords=[
                    Coord(x=0, y=10),
                    Coord(x=0, y=9),
                    Coord(x=1, y=9),
                    Coord(x=1, y=10),
                ]
            ),
            [Coord(x=1, y=10)],
        ),
    ],
)
def test_snake_state_get_self_evading_moves(snake: SnakeState, expected: list[Coord]):
    board_width = 11
    board_height = 11
    moves = snake.get_self_evading_moves(
        board_height=board_height,
        board_width=board_width,
    )
    assert sorted(moves) == sorted(expected)


def test_board_init():
    you = get_mock_snake(
        body_coords=[
            Coord(x=0, y=0),
            Coord(x=0, y=1),
            Coord(x=0, y=2),
        ]
    )
    snakes = [
        you,
        get_mock_snake(
            body_coords=[
                Coord(x=10, y=0),
                Coord(x=10, y=1),
                Coord(x=10, y=2),
            ]
        ),
    ]

    game = Game(
        id=str(uuid.uuid4()),
        ruleset=Ruleset(
            name=str(uuid.uuid4()),
            version=str(uuid.uuid4()),
            settings={"some_key": str(uuid.uuid4())},
        ),
        map=str(uuid.uuid4()),
        timeout=123,
        source="league",
    )

    board = Board(
        height=11,
        width=12,
        food=[Coord(x=1, y=1), Coord(x=10, y=10)],
        hazards=[Coord(x=10, y=1), Coord(x=2, y=10)],
        snakes=snakes,
    )

    gs = GameState(
        game=game,
        turn=12,
        board=board,
        you=you,
    )

    e_gs = EnrichedGameState.from_payload(payload=gs.model_dump())

    # GameState-level assertions
    assert e_gs.current_turn == gs.turn
    assert len(e_gs.turns) == 1

    # Board-level assertions
    assert e_gs.board_height == board.height
    assert e_gs.board_width == board.width
    assert e_gs.turns[0].food == board.food
    assert e_gs.turns[0].hazards == board.hazards
    assert e_gs.turns[0].turn == gs.turn
    assert len(e_gs.snake_defs.keys()) == len(snakes)
    for snake in snakes:
        assert e_gs.snake_defs[snake.id].name == snake.name
        assert e_gs.snake_defs[snake.id].customizations == snake.customizations
        assert e_gs.snake_defs[snake.id].is_self == (snake.id == you.id)

        assert e_gs.turns[0].snake_states[snake.id].health == snake.health
        assert e_gs.turns[0].snake_states[snake.id].body == snake.body
        assert e_gs.turns[0].snake_states[snake.id].latency == snake.latency
        assert e_gs.turns[0].snake_states[snake.id].head == snake.head
        assert e_gs.turns[0].snake_states[snake.id].length == snake.length
        assert e_gs.turns[0].snake_states[snake.id].shout == snake.shout
        assert e_gs.turns[0].snake_states[snake.id].is_self == (snake.id == you.id)

    # Game-level assertions
    assert e_gs.game == gs.game


#
# @pytest.mark.parametrize(
#     "state_prob, body_coords, health, turn, expected",
#     [
#         (  # Left Border: Up -> Right
#             float(100),
#             [
#                 Coord(x=0, y=10),
#                 Coord(x=0, y=9),
#                 Coord(x=0, y=8),
#             ],
#             100,
#             0,
#             {
#                 Coord(x=1, y=10): 100,
#                 Coord(x=0, y=10): 100,
#                 Coord(x=0, y=9): 100,
#             },
#         ),
#         (  # Left Border: Down -> Right
#             float(100),
#             [
#                 Coord(x=0, y=0),
#                 Coord(x=0, y=1),
#                 Coord(x=0, y=2),
#             ],
#             100,
#             0,
#             {
#                 Coord(x=1, y=0): 100,
#                 Coord(x=0, y=0): 100,
#                 Coord(x=0, y=1): 100,
#             },
#         ),
#         (  # Right Border: Up -> Left
#             float(100),
#             [
#                 Coord(x=10, y=10),
#                 Coord(x=10, y=9),
#                 Coord(x=10, y=8),
#             ],
#             100,
#             0,
#             {
#                 Coord(x=9, y=10): 100,
#                 Coord(x=10, y=10): 100,
#                 Coord(x=10, y=9): 100,
#             },
#         ),
#         (  # Right Border: Down -> Left
#             float(100),
#             [
#                 Coord(x=10, y=0),
#                 Coord(x=10, y=1),
#                 Coord(x=10, y=2),
#             ],
#             100,
#             0,
#             {
#                 Coord(x=9, y=0): 100,
#                 Coord(x=10, y=0): 100,
#                 Coord(x=10, y=1): 100,
#             },
#         ),
#         (  # Bottom Border: Left -> Up
#             float(100),
#             [
#                 Coord(x=0, y=0),
#                 Coord(x=1, y=0),
#                 Coord(x=2, y=0),
#             ],
#             100,
#             0,
#             {
#                 Coord(x=0, y=1): 100,
#                 Coord(x=0, y=0): 100,
#                 Coord(x=1, y=0): 100,
#             },
#         ),
#         (  # Bottom Border: Right -> Up
#             float(100),
#             [
#                 Coord(x=10, y=0),
#                 Coord(x=9, y=0),
#                 Coord(x=8, y=0),
#             ],
#             100,
#             0,
#             {
#                 Coord(x=10, y=1): 100,
#                 Coord(x=10, y=0): 100,
#                 Coord(x=9, y=0): 100,
#             },
#         ),
#         (  # Top Border: Left -> Down
#             float(100),
#             [
#                 Coord(x=0, y=10),
#                 Coord(x=1, y=10),
#                 Coord(x=2, y=10),
#             ],
#             100,
#             0,
#             {
#                 Coord(x=0, y=9): 100,
#                 Coord(x=0, y=10): 100,
#                 Coord(x=1, y=10): 100,
#             },
#         ),
#         (  # TopBorder:  Right -> Down
#             float(100),
#             [
#                 Coord(x=10, y=10),
#                 Coord(x=9, y=10),
#                 Coord(x=8, y=10),
#             ],
#             100,
#             0,
#             {
#                 Coord(x=10, y=9): 100,
#                 Coord(x=10, y=10): 100,
#                 Coord(x=9, y=10): 100,
#             },
#         ),
#         (  # Two Options
#             float(100),
#             [
#                 Coord(x=1, y=10),
#                 Coord(x=2, y=10),
#                 Coord(x=3, y=10),
#             ],
#             100,
#             0,
#             {
#                 Coord(x=1, y=9): 50,
#                 Coord(x=0, y=10): 50,
#                 Coord(x=1, y=10): 100,
#                 Coord(x=2, y=10): 100,
#             },
#         ),
#         (  # Three Options
#             float(100),
#             [
#                 Coord(x=1, y=9),
#                 Coord(x=2, y=9),
#                 Coord(x=3, y=9),
#             ],
#             100,
#             0,
#             {
#                 Coord(x=1, y=8): float(100 / 3),
#                 Coord(x=0, y=9): float(100 / 3),
#                 Coord(x=1, y=10): float(100 / 3),
#                 Coord(x=1, y=9): 100,
#                 Coord(x=2, y=9): 100,
#             },
#         ),
#         (  # Ouroboros
#             float(100),
#             [
#                 Coord(x=0, y=10),
#                 Coord(x=0, y=9),
#                 Coord(x=1, y=9),
#                 Coord(x=1, y=10),
#             ],
#             85,
#             7,
#             {
#                 Coord(x=1, y=10): 100,
#                 Coord(x=0, y=10): 100,
#                 Coord(x=0, y=9): 100,
#                 Coord(x=1, y=9): 100,
#             },
#         ),
#     ],
# )
# def test_battlesnake_get_coord_prob_dict(
#     state_prob: float,
#     body_coords: list[Coord],
#     health: int,
#     turn: int,
#     expected: dict[Coord, int],
# ):
#     board_width = 11
#     board_height = 11
#
#     coord_prob_dict = get_coord_prob_dict(
#         state_prob,
#         body_coords=body_coords,
#         health=health,
#         turn=turn,
#         board_width=board_width,
#         board_height=board_height,
#     )
#
#     assert len(coord_prob_dict.keys()) == len(expected.keys())
#     for coord, spam in coord_prob_dict.items():
#         assert expected[coord] == spam.probability
