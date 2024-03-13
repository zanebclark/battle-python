from typing import Any

import numpy as np
import numpy.testing as nptest
import pytest

from battle_python.BoardState import (
    BoardState,
    DEATH_COORD,
    get_board_array,
    get_center_weight_array,
    get_food_array,
    get_all_snake_bodies_array,
    get_snake_heads_at_coord,
    resolve_head_collision,
    resolve_food_consumption,
    get_all_snake_moves_array,
    get_my_snake_area_of_control,
    get_score,
)
from battle_python.SnakeState import SnakeState, Elimination
from battle_python.api_types import Coord
from battle_python.utils import get_aligned_masked_array
from ..mocks.get_mock_board_state import get_mock_board_state
from ..mocks.get_mock_snake_state import get_mock_snake_state


@pytest.fixture
def board_array() -> np.ndarray[Any, np.dtype[np.signedinteger[np._typing._8Bit]]]:
    return np.array(
        [
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
            [99, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 99],
            [99, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 99],
            [99, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 99],
            [99, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 99],
            [99, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 99],
            [99, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 99],
            [99, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 99],
            [99, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 99],
            [99, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 99],
            [99, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 99],
            [99, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 99],
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
        ]
    )


@pytest.fixture
def center_weight_array() -> (
    np.ndarray[Any, np.dtype[np.signedinteger[np._typing._8Bit]]]
):
    return np.array(
        [
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +2, +2, +2, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +2, +2, +2, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +2, +2, +2, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
        ]
    )


def test_get_board_array(
    board_array: np.ndarray[Any, np.dtype[np.signedinteger[np._typing._8Bit]]]
) -> None:
    result = get_board_array(board_width=11, board_height=11)
    nptest.assert_array_equal(result, board_array)


def test_get_center_weight_array(
    board_array: np.ndarray[Any, np.dtype[np.signedinteger[np._typing._8Bit]]]
) -> None:
    result = get_center_weight_array(board_array=board_array)
    expected = np.array(
        [
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +2, +2, +2, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +2, +2, +2, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +2, +2, +2, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
        ]
    )
    nptest.assert_array_equal(result, expected)


@pytest.mark.parametrize(
    "food_coords, expected",
    [
        (
            tuple(),
            np.array(
                [
                    [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                ]
            ),
        ),
        (
            (Coord(x=1, y=1),),
            np.array(
                [
                    [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, 20, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                ]
            ),
        ),
        (
            (
                Coord(x=10, y=10),
                Coord(x=5, y=5),
                Coord(x=1, y=1),
            ),
            np.array(
                [
                    [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 20, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, 20, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, 20, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                ]
            ),
        ),
    ],
)
def test_get_food_array(
    board_array: np.ndarray[Any, np.dtype[np.signedinteger[np._typing._8Bit]]],
    food_coords: tuple[Coord, ...],
    expected: np.ndarray[Any, np.dtype[np.signedinteger[np._typing._8Bit]]],
) -> None:
    result = get_food_array(board_array=board_array, food_coords=food_coords)
    nptest.assert_array_equal(result, expected)


def test_get_food_array_exception(
    board_array: np.ndarray[Any, np.dtype[np.signedinteger[np._typing._8Bit]]]
) -> None:
    with pytest.raises(Exception) as e:
        get_food_array(
            board_array=board_array,
            food_coords=(Coord(x=1, y=15),),
        )
    assert "food coordinate outside of board" in str(e.value)


@pytest.mark.parametrize(
    "snakes, expected",
    [
        (
            (
                get_mock_snake_state(
                    snake_id="Sidecar",
                    body_coords=(
                        Coord(x=1, y=10),
                        Coord(x=1, y=9),
                        Coord(x=1, y=8),
                        Coord(x=1, y=7),
                    ),
                    murder_count=0,
                    health=64,
                ),
                get_mock_snake_state(
                    is_self=True,
                    snake_id="Up -> Right",
                    body_coords=(
                        Coord(x=1, y=10),
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                    ),
                    murder_count=0,
                    health=89,
                ),
            ),
            {
                Coord(x=1, y=10): [
                    get_mock_snake_state(
                        snake_id="Sidecar",
                        body_coords=(
                            Coord(x=1, y=10),
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                        ),
                        murder_count=0,
                        health=64,
                    ),
                    get_mock_snake_state(
                        is_self=True,
                        snake_id="Up -> Right",
                        body_coords=(
                            Coord(x=1, y=10),
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                        ),
                        murder_count=0,
                        health=89,
                    ),
                ]
            },
        ),
        (
            (
                get_mock_snake_state(
                    snake_id="Sidecar",
                    body_coords=(
                        Coord(x=1, y=9),
                        Coord(x=1, y=8),
                        Coord(x=1, y=7),
                    ),
                    murder_count=0,
                    health=64,
                ),
                get_mock_snake_state(
                    is_self=True,
                    snake_id="Up -> Right",
                    body_coords=(
                        Coord(x=1, y=10),
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                    ),
                    murder_count=0,
                    health=89,
                ),
            ),
            {
                Coord(x=1, y=10): [
                    get_mock_snake_state(
                        is_self=True,
                        snake_id="Up -> Right",
                        body_coords=(
                            Coord(x=1, y=10),
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                        ),
                        murder_count=0,
                        health=89,
                    ),
                ],
                Coord(x=1, y=9): [
                    get_mock_snake_state(
                        snake_id="Sidecar",
                        body_coords=(
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                        ),
                        murder_count=0,
                        health=64,
                    ),
                ],
            },
        ),
    ],
)
def test_get_snake_heads_at_coord(
    snakes: tuple[SnakeState, ...], expected: dict[Coord, list[SnakeState]]
) -> None:
    result = get_snake_heads_at_coord(snakes=snakes)
    assert result == expected


@pytest.mark.parametrize(
    "snake_heads_at_coord, expected",
    [
        (
            [
                get_mock_snake_state(
                    snake_id="Equal - 1",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ),
                    is_self=True,
                ),
                get_mock_snake_state(
                    snake_id="Equal - 2",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                    ),
                ),
            ],
            [
                get_mock_snake_state(
                    snake_id="Equal - 1",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ),
                    is_self=True,
                    elimination=Elimination(cause="head-collision", by="Equal - 2"),
                ),
                get_mock_snake_state(
                    snake_id="Equal - 2",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                    ),
                    elimination=Elimination(cause="head-collision", by="Equal - 1"),
                ),
            ],
        ),
        (
            [
                get_mock_snake_state(
                    snake_id="Shorter",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ),
                    is_self=True,
                ),
                get_mock_snake_state(
                    snake_id="Longer",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                        Coord(x=3, y=10),
                    ),
                ),
            ],
            [
                get_mock_snake_state(
                    snake_id="Longer",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                        Coord(x=3, y=10),
                    ),
                    murder_count=1,
                ),
                get_mock_snake_state(
                    snake_id="Shorter",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ),
                    is_self=True,
                    elimination=Elimination(cause="head-collision", by="Longer"),
                ),
            ],
        ),
    ],
)
def test_resolve_head_collision(
    snake_heads_at_coord: list[SnakeState], expected: list[SnakeState]
) -> None:
    resolve_head_collision(snake_heads_at_coord)
    assert snake_heads_at_coord == expected


@pytest.mark.parametrize(
    "snake_heads_at_coord, food_coords, expected_snake_states, expected_food_coords",
    [
        (
            [
                get_mock_snake_state(
                    snake_id="Equal - 1",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ),
                    is_self=True,
                ),
            ],
            tuple(),
            [
                get_mock_snake_state(
                    snake_id="Equal - 1",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ),
                    is_self=True,
                ),
            ],
            tuple(),
        ),
        (
            [
                get_mock_snake_state(
                    snake_id="Equal - 1",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ),
                    is_self=True,
                ),
            ],
            (Coord(x=0, y=10), Coord(x=5, y=5)),
            [
                get_mock_snake_state(
                    snake_id="Equal - 1",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ),
                    food_consumed=(Coord(x=0, y=10),),
                    is_self=True,
                ),
            ],
            (Coord(x=5, y=5),),
        ),
        (
            [
                get_mock_snake_state(
                    snake_id="Shorter",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ),
                    is_self=True,
                    elimination=Elimination(cause="head-collision", by="Longer"),
                ),
                get_mock_snake_state(
                    snake_id="Longer",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                        Coord(x=3, y=10),
                    ),
                    murder_count=1,
                ),
            ],
            (Coord(x=0, y=10), Coord(x=5, y=5)),
            [
                get_mock_snake_state(
                    snake_id="Shorter",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ),
                    is_self=True,
                    elimination=Elimination(cause="head-collision", by="Longer"),
                ),
                get_mock_snake_state(
                    snake_id="Longer",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                        Coord(x=3, y=10),
                    ),
                    food_consumed=(Coord(x=0, y=10),),
                    murder_count=1,
                ),
            ],
            (Coord(x=5, y=5),),
        ),
    ],
)
def test_resolve_food_consumption(
    snake_heads_at_coord: list[SnakeState],
    food_coords: tuple[Coord, ...],
    expected_snake_states: list[SnakeState],
    expected_food_coords: tuple[Coord, ...],
) -> None:
    food_coords = resolve_food_consumption(
        coord=Coord(x=0, y=10),
        snake_heads_at_coord=snake_heads_at_coord,
        food_coords=food_coords,
    )
    assert food_coords == expected_food_coords
    for index, snake in enumerate(snake_heads_at_coord):
        assert snake == expected_snake_states[index]


@pytest.mark.parametrize(
    "snakes, expected",
    [
        (
            (
                get_mock_snake_state(
                    snake_id="Sidecar",
                    body_coords=(
                        Coord(x=1, y=9),
                        Coord(x=1, y=8),
                        Coord(x=1, y=7),
                        Coord(x=1, y=6),
                    ),
                    murder_count=0,
                    health=64,
                ),
            ),
            np.array(
                [
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, +0, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ]
                ]
            ),
        ),
        (
            (
                get_mock_snake_state(
                    snake_id="Sidecar",
                    body_coords=(
                        Coord(x=1, y=9),
                        Coord(x=1, y=8),
                        Coord(x=1, y=7),
                        Coord(x=1, y=6),
                    ),
                    murder_count=0,
                    health=64,
                ),
                get_mock_snake_state(
                    is_self=True,
                    snake_id="Up -> Right",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ),
                    murder_count=0,
                    health=89,
                ),
            ),
            np.array(
                [
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 90, +0, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ],
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, +0, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 90, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ],
                ]
            ),
        ),
        (
            (
                get_mock_snake_state(
                    snake_id="Sidecar",
                    body_coords=(
                        Coord(x=1, y=9),
                        Coord(x=1, y=8),
                        Coord(x=1, y=7),
                        Coord(x=1, y=6),
                    ),
                    murder_count=0,
                    health=64,
                ),
                get_mock_snake_state(
                    snake_id="dead",
                    body_coords=(DEATH_COORD,),
                    murder_count=0,
                    health=64,
                ),
            ),
            np.array(
                [
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, +0, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ]
                ]
            ),
        ),
        (
            (
                get_mock_snake_state(
                    snake_id="Sidecar",
                    body_coords=(
                        Coord(x=1, y=10),
                        Coord(x=1, y=9),
                        Coord(x=1, y=8),
                        Coord(x=1, y=7),
                    ),
                    murder_count=0,
                    health=64,
                ),
                get_mock_snake_state(
                    is_self=True,
                    snake_id="Up -> Right",
                    body_coords=(
                        Coord(x=1, y=10),
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                    ),
                    murder_count=0,
                    health=89,
                ),
            ),
            np.array(
                [
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, 90, +0, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ],
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, 90, +0, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ],
                ]
            ),
        ),
    ],
)
def test_get_all_snake_bodies_array(
    board_array: np.ndarray[Any, np.dtype[np.signedinteger[np._typing._8Bit]]],
    snakes: tuple[SnakeState, ...],
    expected: np.ndarray[Any, np.dtype[np.signedinteger[np._typing._8Bit]]],
) -> None:
    result = get_all_snake_bodies_array(board_array=board_array, snakes=snakes)
    nptest.assert_array_equal(result, expected)


def test_get_all_snake_bodies_array_exception(
    board_array: np.ndarray[Any, np.dtype[np.signedinteger[np._typing._8Bit]]],
) -> None:
    with pytest.raises(Exception) as e:
        get_all_snake_bodies_array(
            board_array=board_array,
            snakes=(
                get_mock_snake_state(
                    snake_id="Sidecar",
                    body_coords=(
                        Coord(x=1, y=13),
                        Coord(x=1, y=14),
                        Coord(x=1, y=15),
                    ),
                    murder_count=0,
                    health=64,
                ),
            ),
        )
    assert "body coordinates outside of board" in str(e.value)


@pytest.mark.parametrize(
    "all_snake_bodies_array, expected",
    [
        (
            np.array(
                [
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, +0, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ]
                ]
            ),
            np.array(
                [
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, +2, +1, +2, +3, +4, +5, +6, +7, +8, +9, 10, 99],
                        [99, +1, +0, +1, +2, +3, +4, +5, +6, +7, +8, +9, 99],
                        [99, +2, 90, +2, +3, +4, +5, +6, +7, +8, +9, 10, 99],
                        [99, +3, 90, +3, +4, +5, +6, +7, +8, +9, 10, 11, 99],
                        [99, +4, 90, +4, +5, +6, +7, +8, +9, 10, 11, 12, 99],
                        [99, +5, +6, +5, +6, +7, +8, +9, 10, 11, 12, 13, 99],
                        [99, +6, +7, +6, +7, +8, +9, 10, 11, 12, 13, 14, 99],
                        [99, +7, +8, +7, +8, +9, 10, 11, 12, 13, 14, 15, 99],
                        [99, +8, +9, +8, +9, 10, 11, 12, 13, 14, 15, 16, 99],
                        [99, +9, 10, +9, 10, 11, 12, 13, 14, 15, 16, 17, 99],
                        [99, 10, 11, 10, 11, 12, 13, 14, 15, 16, 17, 18, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ]
                ]
            ),
        ),
        (
            np.array(
                [
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 90, +0, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 90, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ],
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, +0, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 90, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 90, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ],
                ]
            ),
            np.array(
                [
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, 90, +1, +2, +3, +4, +5, +6, +7, +8, +9, 10, 99],
                        [99, 90, +0, +1, +2, +3, +4, +5, +6, +7, +8, +9, 99],
                        [99, 90, 90, +2, +3, +4, +5, +6, +7, +8, +9, 10, 99],
                        [99, +9, 90, +3, +4, +5, +6, +7, +8, +9, 10, 11, 99],
                        [99, +8, 90, +4, +5, +6, +7, +8, +9, 10, 11, 12, 99],
                        [99, +7, +6, +5, +6, +7, +8, +9, 10, 11, 12, 13, 99],
                        [99, +8, +7, +6, +7, +8, +9, 10, 11, 12, 13, 14, 99],
                        [99, +9, +8, +7, +8, +9, 10, 11, 12, 13, 14, 15, 99],
                        [99, 10, +9, +8, +9, 10, 11, 12, 13, 14, 15, 16, 99],
                        [99, 11, 10, +9, 10, 11, 12, 13, 14, 15, 16, 17, 99],
                        [99, 12, 11, 10, 11, 12, 13, 14, 15, 16, 17, 18, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ],
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, +0, +1, +2, +3, +4, +5, +6, +7, +8, +9, 10, 99],
                        [99, 90, 90, +3, +4, +5, +6, +7, +8, +9, 10, 11, 99],
                        [99, 90, 90, +4, +5, +6, +7, +8, +9, 10, 11, 12, 99],
                        [99, 11, 90, +5, +6, +7, +8, +9, 10, 11, 12, 13, 99],
                        [99, 10, 90, +6, +7, +8, +9, 10, 11, 12, 13, 14, 99],
                        [99, +9, +8, +7, +8, +9, 10, 11, 12, 13, 14, 15, 99],
                        [99, 10, +9, +8, +9, 10, 11, 12, 13, 14, 15, 16, 99],
                        [99, 11, 10, +9, 10, 11, 12, 13, 14, 15, 16, 17, 99],
                        [99, 12, 11, 10, 11, 12, 13, 14, 15, 16, 17, 18, 99],
                        [99, 13, 12, 11, 12, 13, 14, 15, 16, 17, 18, 19, 99],
                        [99, 14, 13, 12, 13, 14, 15, 16, 17, 18, 19, 20, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ],
                ]
            ),
        ),
        (
            np.array(
                [
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, +0, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 90, 90, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 88, 90, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 90, 90, 90, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 88, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ]
                ]
            ),
            np.array(
                [
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, +2, +1, +2, +3, +4, +5, +6, +7, +8, +9, 10, 99],
                        [99, +1, +0, +1, +2, +3, +4, +5, +6, +7, +8, +9, 99],
                        [99, +2, 90, 90, 90, +4, +5, +6, +7, +8, +9, 10, 99],
                        [99, +3, 90, +0, 90, +5, +6, +7, +8, +9, 10, 11, 99],
                        [99, +4, 90, 90, 90, +6, +7, +8, +9, 10, 11, 12, 99],
                        [99, +5, +6, +7, +8, +7, +8, +9, 10, 11, 12, 13, 99],
                        [99, +6, +7, +8, +9, +8, +9, 10, 11, 12, 13, 14, 99],
                        [99, +7, +8, +9, 10, +9, 10, 11, 12, 13, 14, 15, 99],
                        [99, +8, +9, 10, 11, 10, 11, 12, 13, 14, 15, 16, 99],
                        [99, +9, 10, 11, 12, 11, 12, 13, 14, 15, 16, 17, 99],
                        [99, 10, 11, 12, 13, 12, 13, 14, 15, 16, 17, 18, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ]
                ]
            ),
        ),
    ],
)
def test_get_all_snake_moves_array(
    all_snake_bodies_array: np.ndarray[
        Any, np.dtype[np.signedinteger[np._typing._8Bit]]
    ],
    expected: np.ndarray[Any, np.dtype[np.signedinteger[np._typing._8Bit]]],
) -> None:
    result = get_all_snake_moves_array(all_snake_bodies_array=all_snake_bodies_array)
    print(get_aligned_masked_array(result[0]))
    print(get_aligned_masked_array(expected[0]))
    nptest.assert_array_equal(result, expected)


@pytest.mark.parametrize(
    "all_snake_moves_array, expected",
    [
        (
            np.array(
                [
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, +2, +1, +2, +3, +4, +5, +6, +7, +8, +9, 10, 99],
                        [99, +1, +0, +1, +2, +3, +4, +5, +6, +7, +8, +9, 99],
                        [99, +2, 90, +2, +3, +4, +5, +6, +7, +8, +9, 10, 99],
                        [99, +3, 90, +3, +4, +5, +6, +7, +8, +9, 10, 11, 99],
                        [99, +4, 90, +4, +5, +6, +7, +8, +9, 10, 11, 12, 99],
                        [99, +5, +6, +5, +6, +7, +8, +9, 10, 11, 12, 13, 99],
                        [99, +6, +7, +6, +7, +8, +9, 10, 11, 12, 13, 14, 99],
                        [99, +7, +8, +7, +8, +9, 10, 11, 12, 13, 14, 15, 99],
                        [99, +8, +9, +8, +9, 10, 11, 12, 13, 14, 15, 16, 99],
                        [99, +9, 10, +9, 10, 11, 12, 13, 14, 15, 16, 17, 99],
                        [99, 10, 11, 10, 11, 12, 13, 14, 15, 16, 17, 18, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ]
                ]
            ),
            np.array(
                [
                    [+0, +0, +0, +0, +0, +0, +0, +0, +0, +0, +0, +0, +0],
                    [+0, +2, +1, +2, +3, +4, +5, +6, +7, +8, +9, 10, +0],
                    [+0, +1, +0, +1, +2, +3, +4, +5, +6, +7, +8, +9, +0],
                    [+0, +2, +0, +2, +3, +4, +5, +6, +7, +8, +9, 10, +0],
                    [+0, +3, +0, +3, +4, +5, +6, +7, +8, +9, 10, 11, +0],
                    [+0, +4, +0, +4, +5, +6, +7, +8, +9, 10, 11, 12, +0],
                    [+0, +5, +6, +5, +6, +7, +8, +9, 10, 11, 12, 13, +0],
                    [+0, +6, +7, +6, +7, +8, +9, 10, 11, 12, 13, 14, +0],
                    [+0, +7, +8, +7, +8, +9, 10, 11, 12, 13, 14, 15, +0],
                    [+0, +8, +9, +8, +9, 10, 11, 12, 13, 14, 15, 16, +0],
                    [+0, +9, 10, +9, 10, 11, 12, 13, 14, 15, 16, 17, +0],
                    [+0, 10, 11, 10, 11, 12, 13, 14, 15, 16, 17, 18, +0],
                    [+0, +0, +0, +0, +0, +0, +0, +0, +0, +0, +0, +0, +0],
                ]
            ),
        ),
        (
            np.array(
                [
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, +2, +1, +2, +3, +4, +5, +6, +7, +8, +9, 10, 99],
                        [99, +1, +0, +1, +2, +3, +4, +5, +6, +7, +8, +9, 99],
                        [99, +2, 90, +2, +3, +4, +5, +6, +7, +8, +9, 10, 99],
                        [99, +3, 90, +3, +4, +5, +6, +7, +8, +9, 10, 11, 99],
                        [99, +4, 90, +4, +5, +6, +7, +8, +9, 10, 11, 12, 99],
                        [99, +5, +6, +5, +6, +7, +8, +9, 10, 11, 12, 13, 99],
                        [99, +6, +7, +6, +7, +8, +9, 10, 11, 12, 90, 14, 99],
                        [99, +7, +8, +7, +8, +9, 10, 11, 12, 13, 90, 15, 99],
                        [99, +8, +9, +8, +9, 10, 11, 12, 13, 14, 90, 16, 99],
                        [99, +9, 10, +9, 10, 11, 12, 13, 14, 15, 90, 17, 99],
                        [99, 10, 11, 10, 11, 12, 13, 14, 15, 16, 17, 18, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ],
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, 15, 14, 13, 12, 11, 10, +9, +8, +7, +6, +7, 99],
                        [99, 14, 90, 12, 11, 10, +9, +8, +7, +6, +5, +6, 99],
                        [99, 13, 90, 11, 10, +9, +8, +7, +6, +5, +4, +5, 99],
                        [99, 12, 90, 10, +9, +8, +7, +6, +5, +4, +3, +4, 99],
                        [99, 11, 90, +9, +8, +7, +6, +5, +4, +3, +2, +3, 99],
                        [99, 10, +9, +8, +7, +6, +5, +4, +3, +2, +1, +2, 99],
                        [99, +9, +8, +7, +6, +5, +4, +3, +2, +1, +0, +1, 99],
                        [99, 10, +9, +8, +7, +6, +5, +4, +3, +2, 90, +2, 99],
                        [99, 11, 10, +9, +8, +7, +6, +5, +4, +3, 90, +3, 99],
                        [99, 12, 11, 10, +9, +8, +7, +6, +5, +4, 90, +4, 99],
                        [99, 13, 12, 11, 10, +9, +8, +7, +6, +5, +0, +5, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ],
                ]
            ),
            np.array(
                [
                    [+0, +0, +0, +0, +0, +0, +0, +0, +0, +0, +0, +0, +0],
                    [+0, +2, +1, +2, +3, +4, +5, +6, +7, +0, +0, +0, +0],
                    [+0, +1, +0, +1, +2, +3, +4, +5, +6, +0, +0, +0, +0],
                    [+0, +2, +0, +2, +3, +4, +5, +6, +0, +0, +0, +0, +0],
                    [+0, +3, +0, +3, +4, +5, +6, +0, +0, +0, +0, +0, +0],
                    [+0, +4, +0, +4, +5, +6, +0, +0, +0, +0, +0, +0, +0],
                    [+0, +5, +6, +5, +6, +0, +0, +0, +0, +0, +0, +0, +0],
                    [+0, +6, +7, +6, +0, +0, +0, +0, +0, +0, +0, +0, +0],
                    [+0, +7, +8, +7, +0, +0, +0, +0, +0, +0, +0, +0, +0],
                    [+0, +8, +9, +8, +0, +0, +0, +0, +0, +0, +0, +0, +0],
                    [+0, +9, 10, +9, +0, +0, +0, +0, +0, +0, +0, +0, +0],
                    [+0, 10, 11, 10, +0, +0, +0, +0, +0, +0, +0, +0, +0],
                    [+0, +0, +0, +0, +0, +0, +0, +0, +0, +0, +0, +0, +0],
                ]
            ),
        ),
    ],
)
def test_get_my_snake_area_of_control(
    all_snake_moves_array: np.ndarray[
        Any, np.dtype[np.signedinteger[np._typing._8Bit]]
    ],
    expected: np.ndarray[Any, np.dtype[np.signedinteger[np._typing._8Bit]]],
) -> None:
    result = get_my_snake_area_of_control(all_snake_moves_array=all_snake_moves_array)
    nptest.assert_array_equal(result, expected)


@pytest.mark.parametrize(
    "all_snake_moves_array, expected",
    [
        (
            np.array(
                [
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, +2, +1, +2, +3, +4, +5, +6, +7, +8, +9, 10, 99],
                        [99, +1, +0, +1, +2, +3, +4, +5, +6, +7, +8, +9, 99],
                        [99, +2, 90, 90, 90, +4, +5, +6, +7, +8, +9, 10, 99],
                        [99, +3, 90, 88, 90, +5, +6, +7, +8, +9, 10, 11, 99],
                        [99, +4, 90, 90, 90, +6, +7, +8, +9, 10, 11, 12, 99],
                        [99, +5, +6, +7, +8, +7, +8, +9, 10, 11, 12, 13, 99],
                        [99, +6, +7, +8, +9, +8, +9, 10, 11, 12, 13, 14, 99],
                        [99, +7, +8, +9, 10, +9, 10, 11, 12, 13, 14, 15, 99],
                        [99, +8, +9, 10, 11, 10, 11, 12, 13, 14, 15, 16, 99],
                        [99, +9, 10, 11, 12, 11, 12, 13, 14, 15, 16, 17, 99],
                        [99, 10, 11, 12, 13, 12, 13, 14, 15, 16, 17, 18, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ]
                ]
            ),
            129,
        ),
        (
            np.array(
                [
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, +2, +1, +2, +3, +4, +5, +6, +7, +8, +9, 10, 99],
                        [99, +1, +0, +1, +2, +3, +4, +5, +6, +7, +8, +9, 99],
                        [99, +2, 90, 90, 90, +4, +5, +6, +7, +8, +9, 10, 99],
                        [99, +3, 90, 88, 90, +5, +6, +7, +8, +9, 10, 11, 99],
                        [99, +4, 90, 90, 90, +6, +7, +8, +9, 10, 11, 12, 99],
                        [99, +5, +6, +7, +8, +7, +8, +9, 10, 11, 12, 13, 99],
                        [99, +6, +7, +8, +9, +8, +9, 10, 11, 12, 90, 14, 99],
                        [99, +7, +8, +9, 10, +9, 10, 11, 12, 13, 90, 15, 99],
                        [99, +8, +9, 10, 11, 10, 11, 12, 13, 14, 90, 16, 99],
                        [99, +9, 10, 11, 12, 11, 12, 13, 14, 15, 90, 17, 99],
                        [99, 10, 11, 12, 13, 12, 13, 14, 15, 16, 17, 18, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ],
                    [
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                        [99, 15, 14, 13, 12, 11, 10, +9, +8, +7, +6, +7, 99],
                        [99, 14, 90, 90, 90, 10, +9, +8, +7, +6, +5, +6, 99],
                        [99, 13, 90, 88, 90, +9, +8, +7, +6, +5, +4, +5, 99],
                        [99, 12, 90, 90, 90, +8, +7, +6, +5, +4, +3, +4, 99],
                        [99, 11, 10, +9, +8, +7, +6, +5, +4, +3, +2, +3, 99],
                        [99, 10, +9, +8, +7, +6, +5, +4, +3, +2, +1, +2, 99],
                        [99, +9, +8, +7, +6, +5, +4, +3, +2, +1, +0, +1, 99],
                        [99, 10, +9, +8, +7, +6, +5, +4, +3, +2, 90, +2, 99],
                        [99, 11, 10, +9, +8, +7, +6, +5, +4, +3, 90, +3, 99],
                        [99, 12, 11, 10, +9, +8, +7, +6, +5, +4, 90, +4, 99],
                        [99, 13, 12, 11, 10, +9, +8, +7, +6, +5, +0, +5, 99],
                        [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
                    ],
                ]
            ),
            47,
        ),
    ],
)
def test_get_score(
    all_snake_moves_array: np.ndarray[
        Any, np.dtype[np.signedinteger[np._typing._8Bit]]
    ],
    expected: np.ndarray[Any, np.dtype[np.signedinteger[np._typing._8Bit]]],
) -> None:
    food_array = np.array(
        [
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +5, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +5, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
        ]
    )
    center_weight_array = np.array(
        [
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +2, +2, +2, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +2, +2, +2, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +2, +2, +2, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, +1, 99],
            [99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
        ]
    )
    result = get_score(
        my_snake=get_mock_snake_state(
            snake_id="Left Border: Up -> Right",
            is_self=True,
            body_coords=(
                Coord(x=0, y=10),
                Coord(x=0, y=9),
                Coord(x=0, y=8),
            ),
            health=100,
        ),
        all_snake_moves_array=all_snake_moves_array,
        food_array=food_array,
        center_weight_array=center_weight_array,
    )
    assert result == expected


@pytest.mark.parametrize(
    "next_body, food_consumed, health, expected_health",
    [
        ((Coord(x=1, y=1),), True, 50, 100),
        ((Coord(x=2, y=1),), False, 50, 34),
        ((Coord(x=3, y=1),), False, 50, 49),
        ((Coord(x=2, y=1),), False, 10, 0),
        ((Coord(x=2, y=1),), True, 200, 100),
    ],
    ids=str,
)
def test_board_state_get_next_health(
    next_body: tuple[Coord, ...],
    food_consumed: bool,
    health: int,
    expected_health: int,
) -> None:
    board_state = get_mock_board_state(
        hazard_damage_rate=15,
        my_snake=get_mock_snake_state(
            body_coords=(DEATH_COORD,),
            health=health,
            is_self=True,
        ),
        hazard_coords=(Coord(x=1, y=1), Coord(x=2, y=1)),
    )
    next_health = board_state.get_next_health(
        next_body=next_body,
        food_consumed=food_consumed,
        snake=board_state.my_snake,
    )
    assert next_health == expected_health


@pytest.mark.parametrize(
    "current_body, expected",
    [
        (
            (Coord(x=1, y=1), Coord(x=1, y=2), Coord(x=1, y=3)),
            (Coord(x=1, y=1), Coord(x=1, y=2), Coord(x=1, y=3), Coord(x=1, y=3)),
        ),
        (
            (Coord(x=2, y=1), Coord(x=2, y=2), Coord(x=2, y=3)),
            (Coord(x=2, y=1), Coord(x=2, y=2), Coord(x=2, y=3)),
        ),
    ],
    ids=str,
)
def test_board_state_get_next_body(
    current_body: tuple[Coord], expected: tuple[Coord]
) -> None:
    board_state = get_mock_board_state(
        food_coords=(Coord(x=1, y=1),),
        my_snake=get_mock_snake_state(
            snake_id="placeholder",
            body_coords=(DEATH_COORD,),
            is_self=True,
        ),
    )
    next_body = board_state.get_next_body(current_body=current_body)
    assert next_body == expected


@pytest.mark.parametrize(
    "next_body, expected",
    [
        ((Coord(x=1, y=1),), True),
        ((Coord(x=2, y=1),), False),
    ],
    ids=str,
)
def test_board_state_is_food_consumed(
    next_body: tuple[Coord, ...], expected: bool
) -> None:
    board_state = get_mock_board_state(
        hazard_damage_rate=15,
        my_snake=get_mock_snake_state(
            snake_id="placeholder",
            body_coords=(DEATH_COORD,),
            is_self=True,
        ),
        food_coords=(Coord(x=1, y=1),),
    )
    food_consumed = board_state.is_food_consumed(next_body=next_body)
    assert expected == food_consumed


@pytest.mark.parametrize(
    "snake, move, expected",
    [
        (
            get_mock_snake_state(
                snake_id="Left Border: Up -> Right",
                is_self=True,
                body_coords=(
                    Coord(x=0, y=10),
                    Coord(x=0, y=9),
                    Coord(x=0, y=8),
                ),
                health=100,
            ),
            Coord(x=1, y=10),
            get_mock_snake_state(
                snake_id="Left Border: Up -> Right",
                is_self=True,
                body_coords=(
                    Coord(x=1, y=10),
                    Coord(x=0, y=10),
                    Coord(x=0, y=9),
                ),
                health=99,
            ),
        ),
        (
            get_mock_snake_state(
                snake_id="Dead",
                is_self=True,
                body_coords=(
                    Coord(x=0, y=10),
                    Coord(x=0, y=9),
                    Coord(x=0, y=8),
                ),
                health=1,
            ),
            Coord(x=1, y=10),
            get_mock_snake_state(
                snake_id="Dead",
                is_self=True,
                body_coords=(
                    Coord(x=1, y=10),
                    Coord(x=0, y=10),
                    Coord(x=0, y=9),
                ),
                elimination=Elimination(cause="out-of-health"),
                health=0,
            ),
        ),
        (
            get_mock_snake_state(
                snake_id="Dead",
                is_self=True,
                body_coords=(
                    Coord(x=0, y=10),
                    Coord(x=0, y=9),
                    Coord(x=0, y=8),
                ),
                health=87,
            ),
            DEATH_COORD,
            get_mock_snake_state(
                snake_id="Dead",
                is_self=True,
                body_coords=(DEATH_COORD,),
                elimination=Elimination(cause="wall-collision"),
                health=86,
            ),
        ),
    ],
)
def test_board_state_get_next_snake_state_for_snake_move(
    snake: SnakeState,
    move: Coord,
    expected: SnakeState,
) -> None:
    board_state = get_mock_board_state(
        hazard_damage_rate=15,
        my_snake=snake,
        food_coords=(Coord(x=1, y=1),),
    )
    result = board_state.get_next_snake_state_for_snake_move(snake=snake, move=move)
    assert result == expected


@pytest.mark.parametrize(
    "snake_state, expected",
    [
        (
            get_mock_snake_state(
                snake_id="Left Border: Down -> Right",
                is_self=True,
                body_coords=(
                    Coord(x=0, y=0),
                    Coord(x=0, y=1),
                    Coord(x=0, y=2),
                ),
                health=100,
            ),
            [
                get_mock_snake_state(
                    snake_id="Left Border: Down -> Right",
                    is_self=True,
                    body_coords=(
                        Coord(x=1, y=0),
                        Coord(x=0, y=0),
                        Coord(x=0, y=1),
                    ),
                    health=99,
                )
            ],
        ),
        (
            get_mock_snake_state(
                snake_id="Right Border: Up -> Left",
                is_self=True,
                body_coords=(
                    Coord(x=10, y=10),
                    Coord(x=10, y=9),
                    Coord(x=10, y=8),
                ),
                health=100,
            ),
            [
                get_mock_snake_state(
                    snake_id="Right Border: Up -> Left",
                    is_self=True,
                    body_coords=(
                        Coord(x=9, y=10),
                        Coord(x=10, y=10),
                        Coord(x=10, y=9),
                    ),
                    health=99,
                )
            ],
        ),
        (
            get_mock_snake_state(
                snake_id="Right Border: Down -> Left",
                is_self=True,
                body_coords=(
                    Coord(x=10, y=0),
                    Coord(x=10, y=1),
                    Coord(x=10, y=2),
                ),
                health=100,
            ),
            [
                get_mock_snake_state(
                    snake_id="Right Border: Down -> Left",
                    is_self=True,
                    body_coords=(
                        Coord(x=9, y=0),
                        Coord(x=10, y=0),
                        Coord(x=10, y=1),
                    ),
                    health=99,
                )
            ],
        ),
        (
            get_mock_snake_state(
                snake_id="Bottom Border: Left -> Up",
                is_self=True,
                body_coords=(
                    Coord(x=0, y=0),
                    Coord(x=1, y=0),
                    Coord(x=2, y=0),
                ),
                health=100,
            ),
            [
                get_mock_snake_state(
                    snake_id="Bottom Border: Left -> Up",
                    is_self=True,
                    body_coords=(
                        Coord(x=0, y=1),
                        Coord(x=0, y=0),
                        Coord(x=1, y=0),
                    ),
                    health=99,
                )
            ],
        ),
        (
            get_mock_snake_state(
                snake_id="Bottom Border: Right -> Up",
                is_self=True,
                body_coords=(
                    Coord(x=10, y=0),
                    Coord(x=9, y=0),
                    Coord(x=8, y=0),
                ),
                health=100,
            ),
            [
                get_mock_snake_state(
                    snake_id="Bottom Border: Right -> Up",
                    is_self=True,
                    body_coords=(
                        Coord(x=10, y=1),
                        Coord(x=10, y=0),
                        Coord(x=9, y=0),
                    ),
                    health=99,
                )
            ],
        ),
        (
            get_mock_snake_state(
                snake_id="Top Border: Left -> Down",
                is_self=True,
                body_coords=(
                    Coord(x=0, y=10),
                    Coord(x=1, y=10),
                    Coord(x=2, y=10),
                ),
                health=100,
            ),
            [
                get_mock_snake_state(
                    snake_id="Top Border: Left -> Down",
                    is_self=True,
                    body_coords=(
                        Coord(x=0, y=9),
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                    ),
                    health=99,
                )
            ],
        ),
        (
            get_mock_snake_state(
                snake_id="TopBorder:  Right -> Down",
                is_self=True,
                body_coords=(
                    Coord(x=10, y=10),
                    Coord(x=9, y=10),
                    Coord(x=8, y=10),
                ),
                health=100,
            ),
            [
                get_mock_snake_state(
                    snake_id="TopBorder:  Right -> Down",
                    is_self=True,
                    body_coords=(
                        Coord(x=10, y=9),
                        Coord(x=10, y=10),
                        Coord(x=9, y=10),
                    ),
                    health=99,
                )
            ],
        ),
        (
            get_mock_snake_state(
                snake_id="Two Options",
                is_self=True,
                body_coords=(
                    Coord(x=1, y=10),
                    Coord(x=2, y=10),
                    Coord(x=3, y=10),
                ),
                health=100,
            ),
            [
                get_mock_snake_state(
                    snake_id="Two Options",
                    is_self=True,
                    body_coords=(
                        Coord(x=1, y=9),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                    ),
                    health=99,
                ),
                get_mock_snake_state(
                    snake_id="Two Options",
                    is_self=True,
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                    ),
                    health=99,
                ),
            ],
        ),
        (
            get_mock_snake_state(
                snake_id="Three Options",
                is_self=True,
                body_coords=(
                    Coord(x=1, y=9),
                    Coord(x=2, y=9),
                    Coord(x=3, y=9),
                ),
                health=100,
            ),
            [
                get_mock_snake_state(
                    snake_id="Three Options",
                    is_self=True,
                    body_coords=(
                        Coord(x=1, y=8),
                        Coord(x=1, y=9),
                        Coord(x=2, y=9),
                    ),
                    health=99,
                ),
                get_mock_snake_state(
                    snake_id="Three Options",
                    is_self=True,
                    body_coords=(
                        Coord(x=0, y=9),
                        Coord(x=1, y=9),
                        Coord(x=2, y=9),
                    ),
                    health=99,
                ),
                get_mock_snake_state(
                    snake_id="Three Options",
                    is_self=True,
                    body_coords=(
                        Coord(x=1, y=10),
                        Coord(x=1, y=9),
                        Coord(x=2, y=9),
                    ),
                    health=99,
                ),
            ],
        ),
        (
            get_mock_snake_state(
                snake_id="Ouroboros",
                is_self=True,
                body_coords=(
                    Coord(x=0, y=10),
                    Coord(x=0, y=9),
                    Coord(x=1, y=9),
                    Coord(x=1, y=10),
                ),
                health=100,
            ),
            [
                get_mock_snake_state(
                    snake_id="Ouroboros",
                    is_self=True,
                    body_coords=(
                        Coord(x=1, y=10),
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=1, y=9),
                    ),
                    health=99,
                )
            ],
        ),
    ],
)
def test_board_state_get_next_snake_states_for_snake(
    snake_state: SnakeState,
    expected: list[SnakeState],
) -> None:
    board_state = get_mock_board_state(
        hazard_damage_rate=15,
        my_snake=snake_state,
        other_snakes=(
            get_mock_snake_state(
                snake_id="Sidecar",
                body_coords=(
                    Coord(x=5, y=6),
                    Coord(x=5, y=5),
                    Coord(x=5, y=4),
                ),
                murder_count=0,
                health=64,
            ),
        ),
        food_coords=(Coord(x=1, y=1),),
    )
    next_states = board_state.get_next_snake_states_for_snake(
        snake=snake_state, index=0
    )

    assert len(next_states) == len(expected)
    for next_state in next_states:
        expected_state: SnakeState | None = None
        for some_expected_state in expected:
            if (
                some_expected_state.id == next_state.id
                and some_expected_state.body == next_state.body
            ):
                expected_state = some_expected_state
                break

        if expected_state is None:
            raise Exception()

        assert next_state == expected_state


@pytest.mark.parametrize(
    "description, board, expected_boards",
    [
        (
            "Equal length snakes. Avoidable body collision and head collision",
            get_mock_board_state(
                board_height=11,
                board_width=11,
                turn=0,
                my_snake=get_mock_snake_state(
                    is_self=True,
                    snake_id="Up -> Right",
                    body_coords=(
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ),
                    murder_count=0,
                    health=89,
                ),
                other_snakes=(
                    get_mock_snake_state(
                        snake_id="Sidecar",
                        body_coords=(
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                        ),
                        murder_count=0,
                        health=64,
                    ),
                ),
            ),
            [
                get_mock_board_state(
                    board_height=11,
                    board_width=11,
                    turn=1,
                    my_snake=get_mock_snake_state(
                        is_self=True,
                        snake_id="Up -> Right",
                        body_coords=(
                            Coord(x=1, y=10),
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                        ),
                        elimination=Elimination(cause="head-collision", by="Sidecar"),
                        murder_count=0,
                        health=88,
                    ),
                    other_snakes=(
                        get_mock_snake_state(
                            snake_id="Sidecar",
                            body_coords=(
                                Coord(x=1, y=10),
                                Coord(x=1, y=9),
                                Coord(x=1, y=8),
                            ),
                            elimination=Elimination(
                                cause="head-collision", by="Up -> Right"
                            ),
                            murder_count=0,
                            health=63,
                        ),
                    ),
                ),
                get_mock_board_state(
                    board_height=11,
                    board_width=11,
                    turn=1,
                    my_snake=get_mock_snake_state(
                        is_self=True,
                        snake_id="Up -> Right",
                        body_coords=(
                            Coord(x=1, y=10),
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                        ),
                        murder_count=0,
                        health=88,
                    ),
                    other_snakes=(
                        get_mock_snake_state(
                            snake_id="Sidecar",
                            body_coords=(
                                Coord(x=2, y=9),
                                Coord(x=1, y=9),
                                Coord(x=1, y=8),
                            ),
                            murder_count=0,
                            health=63,
                        ),
                    ),
                ),
            ],
        ),
        (
            "Different length snakes. Avoidable body collision. Allow head collision",
            get_mock_board_state(
                board_height=11,
                board_width=11,
                turn=0,
                my_snake=get_mock_snake_state(
                    snake_id="Sidecar",
                    body_coords=(
                        Coord(x=1, y=9),
                        Coord(x=1, y=8),
                        Coord(x=1, y=7),
                        Coord(x=1, y=6),
                    ),
                    murder_count=0,
                    health=64,
                ),
                other_snakes=(
                    get_mock_snake_state(
                        is_self=True,
                        snake_id="Up -> Right",
                        body_coords=(
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=0, y=8),
                        ),
                        murder_count=0,
                        health=89,
                    ),
                ),
            ),
            [
                get_mock_board_state(
                    board_height=11,
                    board_width=11,
                    turn=1,
                    my_snake=get_mock_snake_state(
                        snake_id="Sidecar",
                        body_coords=(
                            Coord(x=1, y=10),
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                        ),
                        murder_count=1,
                        health=63,
                    ),
                    other_snakes=(
                        get_mock_snake_state(
                            is_self=True,
                            snake_id="Up -> Right",
                            body_coords=(
                                Coord(x=1, y=10),
                                Coord(x=0, y=10),
                                Coord(x=0, y=9),
                            ),
                            elimination=Elimination(
                                cause="head-collision", by="Sidecar"
                            ),
                            murder_count=0,
                            health=88,
                        ),
                    ),
                ),
                get_mock_board_state(
                    board_height=11,
                    board_width=11,
                    turn=1,
                    my_snake=get_mock_snake_state(
                        snake_id="Sidecar",
                        body_coords=(
                            Coord(x=2, y=9),
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                        ),
                        murder_count=0,
                        health=63,
                    ),
                    other_snakes=(
                        get_mock_snake_state(
                            is_self=True,
                            snake_id="Up -> Right",
                            body_coords=(
                                Coord(x=1, y=10),
                                Coord(x=0, y=10),
                                Coord(x=0, y=9),
                            ),
                            murder_count=0,
                            health=88,
                        ),
                    ),
                ),
            ],
        ),
        (
            "A ménage à trois. Equal lengths",
            get_mock_board_state(
                board_height=11,
                board_width=11,
                turn=0,
                my_snake=get_mock_snake_state(
                    snake_id="Up -> Left",
                    is_self=True,
                    body_coords=(
                        Coord(x=2, y=10),
                        Coord(x=2, y=9),
                        Coord(x=2, y=8),
                    ),
                    murder_count=0,
                    health=22,
                ),
                other_snakes=(
                    get_mock_snake_state(
                        snake_id="Up -> Right",
                        body_coords=(
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=0, y=8),
                        ),
                        murder_count=0,
                        health=89,
                    ),
                    get_mock_snake_state(
                        snake_id="Sidecar",
                        body_coords=(
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                        ),
                        murder_count=0,
                        health=64,
                    ),
                ),
            ),
            [
                get_mock_board_state(
                    board_height=11,
                    board_width=11,
                    turn=1,
                    my_snake=get_mock_snake_state(
                        snake_id="Up -> Left",
                        is_self=True,
                        body_coords=(
                            Coord(x=1, y=10),
                            Coord(x=2, y=10),
                            Coord(x=2, y=9),
                        ),
                        elimination=Elimination(cause="head-collision", by="Sidecar"),
                        murder_count=0,
                        health=21,
                    ),
                    other_snakes=(
                        get_mock_snake_state(
                            snake_id="Up -> Right",
                            body_coords=(
                                Coord(x=1, y=10),
                                Coord(x=0, y=10),
                                Coord(x=0, y=9),
                            ),
                            elimination=Elimination(
                                cause="head-collision", by="Up -> Left"
                            ),
                            murder_count=0,
                            health=88,
                        ),
                        get_mock_snake_state(
                            snake_id="Sidecar",
                            body_coords=(
                                Coord(x=1, y=10),
                                Coord(x=1, y=9),
                                Coord(x=1, y=8),
                            ),
                            elimination=Elimination(
                                cause="head-collision", by="Up -> Left"
                            ),
                            murder_count=0,
                            health=63,
                        ),
                    ),
                ),
                get_mock_board_state(
                    board_height=11,
                    board_width=11,
                    turn=1,
                    my_snake=get_mock_snake_state(
                        snake_id="Up -> Left",
                        is_self=True,
                        body_coords=(
                            Coord(x=3, y=10),
                            Coord(x=2, y=10),
                            Coord(x=2, y=9),
                        ),
                        murder_count=0,
                        health=21,
                    ),
                    other_snakes=(
                        get_mock_snake_state(
                            snake_id="Up -> Right",
                            body_coords=(
                                Coord(x=1, y=10),
                                Coord(x=0, y=10),
                                Coord(x=0, y=9),
                            ),
                            elimination=Elimination(
                                cause="head-collision", by="Sidecar"
                            ),
                            murder_count=0,
                            health=88,
                        ),
                        get_mock_snake_state(
                            snake_id="Sidecar",
                            body_coords=(
                                Coord(x=1, y=10),
                                Coord(x=1, y=9),
                                Coord(x=1, y=8),
                            ),
                            elimination=Elimination(
                                cause="head-collision", by="Up -> Right"
                            ),
                            murder_count=0,
                            health=63,
                        ),
                    ),
                ),
            ],
        ),
    ],
)
def test_board_state_populate_next_boards(
    description: str,
    board: BoardState,
    expected_boards: list[BoardState],
) -> None:
    board.populate_next_boards()
    for next_board in board.next_boards:
        expected_board = None
        for some_board in expected_boards:
            if next_board.get_other_key() == some_board.get_other_key():
                expected_board = some_board

        if expected_board is None:
            raise Exception()

        assert next_board == expected_board
