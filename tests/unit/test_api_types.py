import pytest
from battle_python.api_types import Coord


def test_coord_get_adjacent() -> None:
    x = 5
    y = 1

    coord = Coord(x=x, y=y)
    moves = coord.get_adjacent()

    assert len(moves) == 4
    assert Coord(x=x, y=y + 1) in moves
    assert Coord(x=x, y=y - 1) in moves
    assert Coord(x=x - 1, y=y) in moves
    assert Coord(x=x + 1, y=y) in moves


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Coord(x=0, y=0), Coord(x=0, y=0), 0),
        (Coord(x=0, y=0), Coord(x=0, y=10), 100),
        (Coord(x=0, y=10), Coord(x=0, y=0), 100),
        (Coord(x=0, y=0), Coord(x=10, y=0), 100),
        (Coord(x=10, y=0), Coord(x=0, y=0), 100),
        (Coord(x=0, y=0), Coord(x=1, y=1), 2),
        (Coord(x=1, y=1), Coord(x=0, y=0), 2),
    ],
    ids=str,
)
def test_coord_relative_distance(a: Coord, b: Coord, expected: int) -> None:
    result = a.get_relative_distance(b)
    assert result == expected


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Coord(x=0, y=0), Coord(x=0, y=0), 0),
        (Coord(x=0, y=0), Coord(x=0, y=10), 10),
        (Coord(x=0, y=10), Coord(x=0, y=0), 10),
        (Coord(x=0, y=0), Coord(x=10, y=0), 10),
        (Coord(x=10, y=0), Coord(x=0, y=0), 10),
        (Coord(x=0, y=0), Coord(x=1, y=1), 2),
        (Coord(x=1, y=1), Coord(x=0, y=0), 2),
        (Coord(x=0, y=0), Coord(x=10, y=10), 20),
        (Coord(x=10, y=10), Coord(x=0, y=0), 20),
    ],
    ids=str,
)
def test_coord_get_manhattan_distance(a: Coord, b: Coord, expected: int) -> None:
    result = a.get_manhattan_distance(b)
    assert result == expected
