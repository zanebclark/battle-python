import pytest

from battle_python.api_types import (
    Coord,
    get_board_coords,
    is_snake_growing,
    Direction,
    get_body_evading_moves,
    get_coord_prob_dict,
)
from ..mocks.mock_api_types import (
    get_mock_battlesnake,
    get_mock_standard_board,
)


def test_get_board_coords():
    board_height = 11
    board_width = 11

    coords = get_board_coords(board_height=board_height, board_width=board_width)

    for x in range(board_width):
        for y in range(board_height):
            assert Coord(x=x, y=y) in coords


def test_board_mark_your_snake():
    you = get_mock_battlesnake(
        is_self=True,
        body_coords=[(2, 0), (1, 0), (0, 0)],
    )

    board = get_mock_standard_board(
        snakes=[
            you,
            get_mock_battlesnake(
                body_coords=[(3, 1), (2, 1), (1, 1), (0, 1)],
            ),
        ],
    )

    board.mark_your_snake(your_snake_id=you.id)
    for snake in board.snakes:
        if snake.id != you.id:
            assert not snake.is_self
        else:
            assert snake.is_self


def test_board_init():
    board = get_mock_standard_board(
        snakes=[
            get_mock_battlesnake(
                is_self=True,
                body_coords=[(3, 1), (2, 1), (1, 1), (0, 1)],
            ),
            get_mock_battlesnake(
                body_coords=[(3, 1), (2, 1), (1, 1), (0, 1)],
            ),
        ],
    )

    assert len(board.snake_dict) == 2


@pytest.mark.parametrize(
    "health, turn, expected",
    [
        (100, 0, False),
        (100, 1, True),
        (88, 0, False),
        (88, 1, False),
    ],
)
def test_is_snake_growing(health: int, turn: int, expected: bool):
    assert is_snake_growing(health=health, turn=turn) is expected


@pytest.mark.parametrize(
    "body_coords, snake_growing, expected",
    [
        (  # Left Border: Up -> Right
            [
                Coord(x=0, y=10),
                Coord(x=0, y=9),
                Coord(x=0, y=8),
            ],
            False,
            {Coord(x=1, y=10): "right"},
        ),
        (  # Left Border: Down -> Right
            [
                Coord(x=0, y=0),
                Coord(x=0, y=1),
                Coord(x=0, y=2),
            ],
            False,
            {Coord(x=1, y=0): "right"},
        ),
        (  # Right Border: Up -> Left
            [
                Coord(x=10, y=10),
                Coord(x=10, y=9),
                Coord(x=10, y=8),
            ],
            False,
            {Coord(x=9, y=10): "left"},
        ),
        (  # Right Border: Down -> Left
            [
                Coord(x=10, y=0),
                Coord(x=10, y=1),
                Coord(x=10, y=2),
            ],
            False,
            {Coord(x=9, y=0): "left"},
        ),
        (  # Bottom Border: Left -> Up
            [
                Coord(x=0, y=0),
                Coord(x=1, y=0),
                Coord(x=2, y=0),
            ],
            False,
            {Coord(x=0, y=1): "up"},
        ),
        (  # Bottom Border: Right -> Up
            [
                Coord(x=10, y=0),
                Coord(x=9, y=0),
                Coord(x=8, y=0),
            ],
            False,
            {Coord(x=10, y=1): "up"},
        ),
        (  # Top Border: Left -> Down
            [
                Coord(x=0, y=10),
                Coord(x=1, y=10),
                Coord(x=2, y=10),
            ],
            False,
            {Coord(x=0, y=9): "down"},
        ),
        (  # TopBorder:  Right -> Down
            [
                Coord(x=10, y=10),
                Coord(x=9, y=10),
                Coord(x=8, y=10),
            ],
            False,
            {Coord(x=10, y=9): "down"},
        ),
        # Two Options
        (
            [
                Coord(x=1, y=10),
                Coord(x=2, y=10),
                Coord(x=3, y=10),
            ],
            False,
            {Coord(x=0, y=10): "left", Coord(x=1, y=9): "down"},
        ),
        # Three Options
        (
            [
                Coord(x=1, y=9),
                Coord(x=2, y=9),
                Coord(x=3, y=9),
            ],
            False,
            {Coord(x=1, y=10): "up", Coord(x=0, y=9): "left", Coord(x=1, y=8): "down"},
        ),
        # Ouroboros
        (
            [
                Coord(x=0, y=10),
                Coord(x=0, y=9),
                Coord(x=1, y=9),
                Coord(x=1, y=10),
            ],
            False,
            {Coord(x=1, y=10): "right"},
        ),
    ],
)
def test_get_body_evading_moves(
    body_coords: list[Coord], snake_growing, expected: dict[Coord, Direction]
):
    board_width = 11
    board_height = 11
    moves = get_body_evading_moves(
        body_coords=body_coords,
        snake_growing=snake_growing,
        board_height=board_height,
        board_width=board_width,
    )

    assert moves == expected


@pytest.mark.parametrize(
    "state_prob, body_coords, health, turn, expected",
    [
        (  # Left Border: Up -> Right
            float(100),
            [
                Coord(x=0, y=10),
                Coord(x=0, y=9),
                Coord(x=0, y=8),
            ],
            100,
            0,
            {
                Coord(x=1, y=10): 100,
                Coord(x=0, y=10): 100,
                Coord(x=0, y=9): 100,
            },
        ),
        (  # Left Border: Down -> Right
            float(100),
            [
                Coord(x=0, y=0),
                Coord(x=0, y=1),
                Coord(x=0, y=2),
            ],
            100,
            0,
            {
                Coord(x=1, y=0): 100,
                Coord(x=0, y=0): 100,
                Coord(x=0, y=1): 100,
            },
        ),
        (  # Right Border: Up -> Left
            float(100),
            [
                Coord(x=10, y=10),
                Coord(x=10, y=9),
                Coord(x=10, y=8),
            ],
            100,
            0,
            {
                Coord(x=9, y=10): 100,
                Coord(x=10, y=10): 100,
                Coord(x=10, y=9): 100,
            },
        ),
        (  # Right Border: Down -> Left
            float(100),
            [
                Coord(x=10, y=0),
                Coord(x=10, y=1),
                Coord(x=10, y=2),
            ],
            100,
            0,
            {
                Coord(x=9, y=0): 100,
                Coord(x=10, y=0): 100,
                Coord(x=10, y=1): 100,
            },
        ),
        (  # Bottom Border: Left -> Up
            float(100),
            [
                Coord(x=0, y=0),
                Coord(x=1, y=0),
                Coord(x=2, y=0),
            ],
            100,
            0,
            {
                Coord(x=0, y=1): 100,
                Coord(x=0, y=0): 100,
                Coord(x=1, y=0): 100,
            },
        ),
        (  # Bottom Border: Right -> Up
            float(100),
            [
                Coord(x=10, y=0),
                Coord(x=9, y=0),
                Coord(x=8, y=0),
            ],
            100,
            0,
            {
                Coord(x=10, y=1): 100,
                Coord(x=10, y=0): 100,
                Coord(x=9, y=0): 100,
            },
        ),
        (  # Top Border: Left -> Down
            float(100),
            [
                Coord(x=0, y=10),
                Coord(x=1, y=10),
                Coord(x=2, y=10),
            ],
            100,
            0,
            {
                Coord(x=0, y=9): 100,
                Coord(x=0, y=10): 100,
                Coord(x=1, y=10): 100,
            },
        ),
        (  # TopBorder:  Right -> Down
            float(100),
            [
                Coord(x=10, y=10),
                Coord(x=9, y=10),
                Coord(x=8, y=10),
            ],
            100,
            0,
            {
                Coord(x=10, y=9): 100,
                Coord(x=10, y=10): 100,
                Coord(x=9, y=10): 100,
            },
        ),
        (  # Two Options
            float(100),
            [
                Coord(x=1, y=10),
                Coord(x=2, y=10),
                Coord(x=3, y=10),
            ],
            100,
            0,
            {
                Coord(x=1, y=9): 50,
                Coord(x=0, y=10): 50,
                Coord(x=1, y=10): 100,
                Coord(x=2, y=10): 100,
            },
        ),
        (  # Three Options
            float(100),
            [
                Coord(x=1, y=9),
                Coord(x=2, y=9),
                Coord(x=3, y=9),
            ],
            100,
            0,
            {
                Coord(x=1, y=8): float(100 / 3),
                Coord(x=0, y=9): float(100 / 3),
                Coord(x=1, y=10): float(100 / 3),
                Coord(x=1, y=9): 100,
                Coord(x=2, y=9): 100,
            },
        ),
        (  # Ouroboros
            float(100),
            [
                Coord(x=0, y=10),
                Coord(x=0, y=9),
                Coord(x=1, y=9),
                Coord(x=1, y=10),
            ],
            85,
            7,
            {
                Coord(x=1, y=10): 100,
                Coord(x=0, y=10): 100,
                Coord(x=0, y=9): 100,
                Coord(x=1, y=9): 100,
            },
        ),
    ],
)
def test_battlesnake_get_coord_prob_dict(
    state_prob: float,
    body_coords: list[Coord],
    health: int,
    turn: int,
    expected: dict[Coord, int],
):
    board_width = 11
    board_height = 11

    coord_prob_dict = get_coord_prob_dict(
        state_prob,
        body_coords=body_coords,
        health=health,
        turn=turn,
        board_width=board_width,
        board_height=board_height,
    )

    assert len(coord_prob_dict.keys()) == len(expected.keys())
    for coord, spam in coord_prob_dict.items():
        assert expected[coord] == spam.probability
