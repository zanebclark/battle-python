import pytest
from battle_python.api_types import Coord


def test_coord_get_potential_moves():
    x = 5
    y = 1

    coord = Coord(x=x, y=y)
    moves = coord.get_potential_moves()

    assert moves[Coord(x, y + 1)] == "up"
    assert moves[Coord(x, y - 1)] == "down"
    assert moves[Coord(x - 1, y)] == "left"
    assert moves[Coord(x + 1, y)] == "right"


@pytest.mark.parametrize(
    "coords, expected",
    [
        # Left Border
        ((0, 10), [Coord(x=1, y=10), Coord(x=0, y=9)]),
        ((0, 0), [Coord(x=1, y=0), Coord(x=0, y=1)]),
        # Right Border
        ((10, 10), [Coord(x=9, y=10), Coord(x=10, y=9)]),
        ((10, 0), [Coord(x=9, y=0), Coord(x=10, y=1)]),
        # Bottom Border
        ((0, 0), [Coord(x=0, y=1), Coord(x=1, y=0)]),
        ((10, 0), [Coord(x=10, y=1), Coord(x=9, y=0)]),
        # Top Border
        ((0, 10), [Coord(x=0, y=9), Coord(x=1, y=10)]),
        ((10, 10), [Coord(x=10, y=9), Coord(x=9, y=10)]),
        # Two Options
        ((1, 10), [Coord(x=0, y=10), Coord(x=1, y=9), Coord(x=2, y=10)]),
        # Three Options
        ((1, 9), [Coord(x=1, y=10), Coord(x=0, y=9), Coord(x=1, y=8), Coord(x=2, y=9)]),
    ],
)
def test_coord_get_legal_moves(coords: tuple[int, int], expected: list[Coord]):
    board_width = 11
    board_height = 11
    x, y = coords
    coord = Coord(x=x, y=y)
    legal_moves = coord.get_legal_moves(
        board_height=board_height, board_width=board_width
    )
    assert len(legal_moves) == len(expected)
    for move in legal_moves.keys():
        assert move in expected
