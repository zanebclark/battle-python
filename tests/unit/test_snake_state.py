import pytest

from battle_python.EnrichedBoard import EnrichedBoard
from battle_python.SnakeState import SnakeState
from battle_python.api_types import (
    Coord,
)
from mocks.get_mock_enriched_board import get_mock_enriched_board
from mocks.get_mock_snake_state import get_mock_snake_state


@pytest.mark.parametrize(
    "board, expected",
    [
        (  # Left Border: Up -> Right
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        is_self=True,
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=0, y=8),
                        ],
                    )
                ]
            ),
            [Coord(x=1, y=10)],
        ),
        (  # Left Border: Down -> Right
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        is_self=True,
                        body_coords=[
                            Coord(x=0, y=0),
                            Coord(x=0, y=1),
                            Coord(x=0, y=2),
                        ],
                    )
                ]
            ),
            [Coord(x=1, y=0)],
        ),
        (  # Right Border: Up -> Left
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        is_self=True,
                        body_coords=[
                            Coord(x=10, y=10),
                            Coord(x=10, y=9),
                            Coord(x=10, y=8),
                        ],
                    )
                ]
            ),
            [Coord(x=9, y=10)],
        ),
        (  # Right Border: Down -> Left
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        is_self=True,
                        body_coords=[
                            Coord(x=10, y=0),
                            Coord(x=10, y=1),
                            Coord(x=10, y=2),
                        ],
                    )
                ]
            ),
            [Coord(x=9, y=0)],
        ),
        (  # Bottom Border: Left -> Up
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        is_self=True,
                        body_coords=[
                            Coord(x=0, y=0),
                            Coord(x=1, y=0),
                            Coord(x=2, y=0),
                        ],
                    )
                ]
            ),
            [Coord(x=0, y=1)],
        ),
        (  # Bottom Border: Right -> Up
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        is_self=True,
                        body_coords=[
                            Coord(x=10, y=0),
                            Coord(x=9, y=0),
                            Coord(x=8, y=0),
                        ],
                    )
                ]
            ),
            [Coord(x=10, y=1)],
        ),
        (  # Top Border: Left -> Down
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        is_self=True,
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=1, y=10),
                            Coord(x=2, y=10),
                        ],
                    )
                ]
            ),
            [Coord(x=0, y=9)],
        ),
        (  # TopBorder:  Right -> Down
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        is_self=True,
                        body_coords=[
                            Coord(x=10, y=10),
                            Coord(x=9, y=10),
                            Coord(x=8, y=10),
                        ],
                    )
                ]
            ),
            [Coord(x=10, y=9)],
        ),
        # Two Options
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        is_self=True,
                        body_coords=[
                            Coord(x=1, y=10),
                            Coord(x=2, y=10),
                            Coord(x=3, y=10),
                        ],
                    )
                ]
            ),
            [
                Coord(x=0, y=10),
                Coord(x=1, y=9),
            ],
        ),
        # Three Options
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        is_self=True,
                        body_coords=[
                            Coord(x=1, y=9),
                            Coord(x=2, y=9),
                            Coord(x=3, y=9),
                        ],
                    )
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
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        is_self=True,
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=1, y=9),
                            Coord(x=1, y=10),
                        ],
                    )
                ]
            ),
            [Coord(x=1, y=10)],
        ),
        # Collision, equal length
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        snake_id="Sidecar",
                        is_self=True,
                        body_coords=[
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                        ],
                    ),
                    get_mock_snake_state(
                        snake_id="Up -> Right",
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=0, y=8),
                        ],
                    ),
                ]
            ),
            [Coord(x=2, y=9)],
        ),
        # Collision, equal length, no good options
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        snake_id="Up -> Right",
                        is_self=True,
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=0, y=8),
                        ],
                    ),
                    get_mock_snake_state(
                        snake_id="Sidecar",
                        body_coords=[
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                        ],
                    ),
                ]
            ),
            [],
        ),
        # Collision, greater length
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        snake_id="Sidecar",
                        is_self=True,
                        body_coords=[
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                            Coord(x=1, y=6),
                        ],
                    ),
                    get_mock_snake_state(
                        snake_id="Up -> Right",
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=0, y=8),
                        ],
                    ),
                ]
            ),
            [
                Coord(x=2, y=9),
                Coord(x=1, y=10),
            ],
        ),
    ],
)
def test_snake_state_get_reasonable_moves(board: EnrichedBoard, expected: list[Coord]):
    snake: SnakeState | None = None
    for potential_snake in board.snake_states:
        if potential_snake.is_self:
            snake = potential_snake
            break

    if snake is None:
        raise Exception()

    moves = snake.get_reasonable_moves(board=board)
    assert sorted(moves) == sorted(expected)


@pytest.mark.parametrize(
    "board, expected",
    [
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        snake_id="Left Border: Up -> Right",
                        is_self=True,
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=0, y=8),
                        ],
                        health=100,
                    )
                ]
            ),
            [
                get_mock_snake_state(
                    snake_id="Left Border: Up -> Right",
                    is_self=True,
                    body_coords=[
                        Coord(x=1, y=10),
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                    ],
                    health=99,
                )
            ],
        ),
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        snake_id="Left Border: Down -> Right",
                        is_self=True,
                        body_coords=[
                            Coord(x=0, y=0),
                            Coord(x=0, y=1),
                            Coord(x=0, y=2),
                        ],
                        health=100,
                    )
                ]
            ),
            [
                get_mock_snake_state(
                    snake_id="Left Border: Down -> Right",
                    is_self=True,
                    body_coords=[
                        Coord(x=1, y=0),
                        Coord(x=0, y=0),
                        Coord(x=0, y=1),
                    ],
                    health=99,
                )
            ],
        ),
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        snake_id="Right Border: Up -> Left",
                        is_self=True,
                        body_coords=[
                            Coord(x=10, y=10),
                            Coord(x=10, y=9),
                            Coord(x=10, y=8),
                        ],
                        health=100,
                    )
                ]
            ),
            [
                get_mock_snake_state(
                    snake_id="Right Border: Up -> Left",
                    is_self=True,
                    body_coords=[
                        Coord(x=9, y=10),
                        Coord(x=10, y=10),
                        Coord(x=10, y=9),
                    ],
                    health=99,
                )
            ],
        ),
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        snake_id="Right Border: Down -> Left",
                        is_self=True,
                        body_coords=[
                            Coord(x=10, y=0),
                            Coord(x=10, y=1),
                            Coord(x=10, y=2),
                        ],
                        health=100,
                    )
                ]
            ),
            [
                get_mock_snake_state(
                    snake_id="Right Border: Down -> Left",
                    is_self=True,
                    body_coords=[
                        Coord(x=9, y=0),
                        Coord(x=10, y=0),
                        Coord(x=10, y=1),
                    ],
                    health=99,
                )
            ],
        ),
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        snake_id="Bottom Border: Left -> Up",
                        is_self=True,
                        body_coords=[
                            Coord(x=0, y=0),
                            Coord(x=1, y=0),
                            Coord(x=2, y=0),
                        ],
                        health=100,
                    )
                ]
            ),
            [
                get_mock_snake_state(
                    snake_id="Bottom Border: Left -> Up",
                    is_self=True,
                    body_coords=[
                        Coord(x=0, y=1),
                        Coord(x=0, y=0),
                        Coord(x=1, y=0),
                    ],
                    health=99,
                )
            ],
        ),
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        snake_id="Bottom Border: Right -> Up",
                        is_self=True,
                        body_coords=[
                            Coord(x=10, y=0),
                            Coord(x=9, y=0),
                            Coord(x=8, y=0),
                        ],
                        health=100,
                    )
                ]
            ),
            [
                get_mock_snake_state(
                    snake_id="Bottom Border: Right -> Up",
                    is_self=True,
                    body_coords=[
                        Coord(x=10, y=1),
                        Coord(x=10, y=0),
                        Coord(x=9, y=0),
                    ],
                    health=99,
                )
            ],
        ),
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        snake_id="Top Border: Left -> Down",
                        is_self=True,
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=1, y=10),
                            Coord(x=2, y=10),
                        ],
                        health=100,
                    )
                ]
            ),
            [
                get_mock_snake_state(
                    snake_id="Top Border: Left -> Down",
                    is_self=True,
                    body_coords=[
                        Coord(x=0, y=9),
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                    ],
                    health=99,
                )
            ],
        ),
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        snake_id="TopBorder:  Right -> Down",
                        is_self=True,
                        body_coords=[
                            Coord(x=10, y=10),
                            Coord(x=9, y=10),
                            Coord(x=8, y=10),
                        ],
                        health=100,
                    )
                ]
            ),
            [
                get_mock_snake_state(
                    snake_id="TopBorder:  Right -> Down",
                    is_self=True,
                    body_coords=[
                        Coord(x=10, y=9),
                        Coord(x=10, y=10),
                        Coord(x=9, y=10),
                    ],
                    health=99,
                )
            ],
        ),
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        snake_id="Two Options",
                        is_self=True,
                        body_coords=[
                            Coord(x=1, y=10),
                            Coord(x=2, y=10),
                            Coord(x=3, y=10),
                        ],
                        health=100,
                    )
                ]
            ),
            [
                get_mock_snake_state(
                    snake_id="Two Options",
                    is_self=True,
                    state_prob=float(1 / 2),
                    body_coords=[
                        Coord(x=1, y=9),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                    ],
                    health=99,
                ),
                get_mock_snake_state(
                    snake_id="Two Options",
                    is_self=True,
                    state_prob=float(1 / 2),
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                    ],
                    health=99,
                ),
            ],
        ),
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        snake_id="Three Options",
                        is_self=True,
                        body_coords=[
                            Coord(x=1, y=9),
                            Coord(x=2, y=9),
                            Coord(x=3, y=9),
                        ],
                        health=100,
                    )
                ]
            ),
            [
                get_mock_snake_state(
                    snake_id="Three Options",
                    is_self=True,
                    state_prob=float(1 / 3),
                    body_coords=[
                        Coord(x=1, y=8),
                        Coord(x=1, y=9),
                        Coord(x=2, y=9),
                    ],
                    health=99,
                ),
                get_mock_snake_state(
                    snake_id="Three Options",
                    is_self=True,
                    state_prob=float(1 / 3),
                    body_coords=[
                        Coord(x=0, y=9),
                        Coord(x=1, y=9),
                        Coord(x=2, y=9),
                    ],
                    health=99,
                ),
                get_mock_snake_state(
                    snake_id="Three Options",
                    is_self=True,
                    state_prob=float(1 / 3),
                    body_coords=[
                        Coord(x=1, y=10),
                        Coord(x=1, y=9),
                        Coord(x=2, y=9),
                    ],
                    health=99,
                ),
            ],
        ),
        (
            get_mock_enriched_board(
                snake_states=[
                    get_mock_snake_state(
                        snake_id="Ouroboros",
                        is_self=True,
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=1, y=9),
                            Coord(x=1, y=10),
                        ],
                        health=100,
                    )
                ]
            ),
            [
                get_mock_snake_state(
                    snake_id="Ouroboros",
                    is_self=True,
                    body_coords=[
                        Coord(x=1, y=10),
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=1, y=9),
                    ],
                    health=99,
                )
            ],
        ),
    ],
)  # TODO: Test no health prob
def test_snake_get_next_states(
    board: EnrichedBoard,
    expected: list[SnakeState],
):
    snake: SnakeState | None = None
    for potential_snake in board.snake_states:
        if potential_snake.is_self:
            snake = potential_snake
            break

    if snake is None:
        raise Exception()

    next_states = snake.get_next_states(board=board)

    assert len(next_states) == len(expected)
    for next_state in next_states:
        expected_state: SnakeState | None = None
        for some_expected_state in expected:
            if (
                some_expected_state.snake_id == next_state.snake_id
                and some_expected_state.body == next_state.body
            ):
                expected_state = some_expected_state
                break

        if expected_state is None:
            raise Exception()

        assert next_state.state_prob == expected_state.state_prob
        assert next_state.health == expected_state.health
        assert next_state.body == expected_state.body
        assert next_state.head == expected_state.head
        assert next_state.length == expected_state.length
        assert next_state.prev_state == snake
