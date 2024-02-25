import pytest

from battle_python.api_types import Coord
from ..mocks.get_mock_snake_state import get_mock_snake_state


class TestSnakeState:
    @pytest.mark.parametrize(
        "body, expected",
        [
            ((Coord(x=5, y=5), Coord(x=5, y=4)), Coord(x=0, y=1)),
            ((Coord(x=5, y=5), Coord(x=5, y=6)), Coord(x=0, y=-1)),
            ((Coord(x=5, y=5), Coord(x=4, y=5)), Coord(x=1, y=0)),
            ((Coord(x=5, y=5), Coord(x=6, y=5)), Coord(x=-1, y=0)),
        ],
        ids=str,
    )
    def test_last_move(self, body: tuple[Coord, ...], expected: Coord):
        snake = get_mock_snake_state(body_coords=body)
        result = snake.last_move
        assert result == expected
