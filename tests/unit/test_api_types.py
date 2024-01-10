from battle_python.api_types import Coord


def test_coord_get_adjacent():
    x = 5
    y = 1

    coord = Coord(x=x, y=y)
    moves = coord.get_adjacent()

    assert len(moves) == 4
    assert Coord(x=x, y=y + 1) in moves
    assert Coord(x=x, y=y - 1) in moves
    assert Coord(x=x - 1, y=y) in moves
    assert Coord(x=x + 1, y=y) in moves
