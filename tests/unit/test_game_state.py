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
    gs_snakes = [*e_gs.turns[0].snake_states]
    for snake in snakes:
        assert e_gs.snake_defs[snake.id].name == snake.name
        assert e_gs.snake_defs[snake.id].customizations == snake.customizations
        assert e_gs.snake_defs[snake.id].is_self == (snake.id == you.id)

        gs_snake: SnakeState | None = None
        for index, some_snake in enumerate(gs_snakes):
            if some_snake.snake_id == snake.id:
                gs_snake = gs_snakes.pop(index)
                break

        if not gs_snake:
            raise Exception(f"snake not found: {snake.id}")

        assert gs_snake.probability == 100
        assert gs_snake.health == snake.health
        assert gs_snake.body == snake.body
        assert gs_snake.latency == int(snake.latency)
        assert gs_snake.head == snake.head
        assert gs_snake.length == snake.length
        assert gs_snake.shout == snake.shout
        assert gs_snake.is_self == (snake.id == you.id)

    # Game-level assertions
    assert e_gs.game == gs.game


@pytest.mark.parametrize(
    "snake_state, expected",
    [
        (  # Left Border: Up -> Right
            get_mock_snake_state(
                probability=float(100),
                body_coords=[
                    Coord(x=0, y=10),
                    Coord(x=0, y=9),
                    Coord(x=0, y=8),
                ],
                health=100,
            ),
            [
                get_mock_snake_state(
                    probability=float(100),
                    body_coords=[
                        Coord(x=1, y=10),
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                    ],
                    health=99,
                )
            ],
        ),
        (  # Left Border: Down -> Right
            get_mock_snake_state(
                probability=float(100),
                body_coords=[
                    Coord(x=0, y=0),
                    Coord(x=0, y=1),
                    Coord(x=0, y=2),
                ],
                health=100,
            ),
            [
                get_mock_snake_state(
                    probability=float(100),
                    body_coords=[
                        Coord(x=1, y=0),
                        Coord(x=0, y=0),
                        Coord(x=0, y=1),
                    ],
                    health=99,
                )
            ],
        ),
        (  # Right Border: Up -> Left
            get_mock_snake_state(
                probability=float(100),
                body_coords=[
                    Coord(x=10, y=10),
                    Coord(x=10, y=9),
                    Coord(x=10, y=8),
                ],
                health=100,
            ),
            [
                get_mock_snake_state(
                    probability=float(100),
                    body_coords=[
                        Coord(x=9, y=10),
                        Coord(x=10, y=10),
                        Coord(x=10, y=9),
                    ],
                    health=99,
                )
            ],
        ),
        (  # Right Border: Down -> Left
            get_mock_snake_state(
                probability=float(100),
                body_coords=[
                    Coord(x=10, y=0),
                    Coord(x=10, y=1),
                    Coord(x=10, y=2),
                ],
                health=100,
            ),
            [
                get_mock_snake_state(
                    probability=float(100),
                    body_coords=[
                        Coord(x=9, y=0),
                        Coord(x=10, y=0),
                        Coord(x=10, y=1),
                    ],
                    health=99,
                )
            ],
        ),
        (  # Bottom Border: Left -> Up
            get_mock_snake_state(
                probability=float(100),
                body_coords=[
                    Coord(x=0, y=0),
                    Coord(x=1, y=0),
                    Coord(x=2, y=0),
                ],
                health=100,
            ),
            [
                get_mock_snake_state(
                    probability=float(100),
                    body_coords=[
                        Coord(x=0, y=1),
                        Coord(x=0, y=0),
                        Coord(x=1, y=0),
                    ],
                    health=99,
                )
            ],
        ),
        (  # Bottom Border: Right -> Up
            get_mock_snake_state(
                probability=float(100),
                body_coords=[
                    Coord(x=10, y=0),
                    Coord(x=9, y=0),
                    Coord(x=8, y=0),
                ],
                health=100,
            ),
            [
                get_mock_snake_state(
                    probability=float(100),
                    body_coords=[
                        Coord(x=10, y=1),
                        Coord(x=10, y=0),
                        Coord(x=9, y=0),
                    ],
                    health=99,
                )
            ],
        ),
        (  # Top Border: Left -> Down
            get_mock_snake_state(
                probability=float(100),
                body_coords=[
                    Coord(x=0, y=10),
                    Coord(x=1, y=10),
                    Coord(x=2, y=10),
                ],
                health=100,
            ),
            [
                get_mock_snake_state(
                    probability=float(100),
                    body_coords=[
                        Coord(x=0, y=9),
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                    ],
                    health=100,
                )
            ],
        ),
        (  # TopBorder:  Right -> Down
            get_mock_snake_state(
                probability=float(100),
                body_coords=[
                    Coord(x=10, y=10),
                    Coord(x=9, y=10),
                    Coord(x=8, y=10),
                ],
                health=100,
            ),
            [
                get_mock_snake_state(
                    probability=float(100),
                    body_coords=[
                        Coord(x=10, y=9),
                        Coord(x=10, y=10),
                        Coord(x=9, y=10),
                    ],
                    health=99,
                )
            ],
        ),
        (  # Two Options
            get_mock_snake_state(
                probability=float(100),
                body_coords=[
                    Coord(x=1, y=10),
                    Coord(x=2, y=10),
                    Coord(x=3, y=10),
                ],
                health=100,
            ),
            [
                get_mock_snake_state(
                    probability=float(50),
                    body_coords=[
                        Coord(x=1, y=9),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                    ],
                    health=99,
                ),
                get_mock_snake_state(
                    probability=float(50),
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                    ],
                    health=99,
                ),
            ],
        ),
        (  # Three Options
            get_mock_snake_state(
                probability=float(100),
                body_coords=[
                    Coord(x=1, y=9),
                    Coord(x=2, y=9),
                    Coord(x=3, y=9),
                ],
            ),
            [
                get_mock_snake_state(
                    probability=float(100 / 3),
                    body_coords=[
                        Coord(x=1, y=8),
                        Coord(x=1, y=9),
                        Coord(x=2, y=9),
                    ],
                    health=99,
                ),
                get_mock_snake_state(
                    probability=float(100 / 3),
                    body_coords=[
                        Coord(x=0, y=9),
                        Coord(x=1, y=9),
                        Coord(x=2, y=9),
                    ],
                    health=99,
                ),
                get_mock_snake_state(
                    probability=float(100 / 3),
                    body_coords=[
                        Coord(x=1, y=10),
                        Coord(x=1, y=9),
                        Coord(x=2, y=9),
                    ],
                    health=99,
                ),
            ],
        ),
        (  # Ouroboros
            get_mock_snake_state(
                probability=float(100),
                body_coords=[
                    Coord(x=0, y=10),
                    Coord(x=0, y=9),
                    Coord(x=1, y=9),
                    Coord(x=1, y=10),
                ],
            ),
            [
                get_mock_snake_state(
                    probability=float(100),
                    body_coords=[
                        Coord(x=1, y=10),
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=1, y=9),
                    ],
                )
            ],
        ),
    ],
)  # TODO: Test no health prob
def test_snake_get_next_states(
    snake_state: SnakeState,
    expected: list[SnakeState],
):
    board_width = 11
    board_height = 11

    next_states = snake_state.get_next_states(
        board_width=board_width,
        board_height=board_height,
    )

    assert len(next_states) == len(expected)
    for next_state in next_states:
        for expected_state in expected:
            if expected_state.snake_id != next_state.snake_id:
                continue

            assert next_state.probability == expected_state.probability
            assert next_state.health == expected_state.health
            assert next_state.body == expected_state.body
            assert next_state.head == expected_state.head
            assert next_state.length == expected_state.length
            assert next_state.prev_state == snake_state
