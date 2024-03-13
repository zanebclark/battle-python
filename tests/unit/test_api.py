import pytest
from fastapi.testclient import TestClient

from battle_python.GameState import GameState
from battle_python.api_types import Coord, SnakeDef, SnakeCustomizations
from battle_python.main import api
from ..mocks.get_mock_game_state import get_mock_game_state
from ..mocks.get_mock_snake_state import get_mock_snake_state

client = TestClient(api)


@pytest.fixture
def game_state() -> GameState:
    return get_mock_game_state(
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
                is_self=True,
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
    )


def test_populated_battlesnake_details() -> None:
    response = client.get("/")
    data = response.json()

    assert response.status_code == 200
    assert data["apiversion"] == "1"
    assert data["author"] is not None
    assert data["color"] is not None
    assert data["head"] is not None
    assert data["tail"] is not None
    assert data["version"] is not None


def test_game_started(game_state: GameState) -> None:
    body = game_state.current_board.get_move_request(
        snake_defs=game_state.snake_defs, game=game_state.game
    )
    response = client.post("/start", json=body)
    assert response.status_code == 200


def test_move(game_state: GameState) -> None:
    body = game_state.current_board.get_move_request(
        snake_defs=game_state.snake_defs, game=game_state.game
    )
    response = client.post("/move", json=body)
    assert response.status_code == 200


def test_end(game_state: GameState) -> None:
    body = game_state.current_board.get_move_request(
        snake_defs=game_state.snake_defs, game=game_state.game
    )
    response = client.post("/end", json=body)
    assert response.status_code == 200
