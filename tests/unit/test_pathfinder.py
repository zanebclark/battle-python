import pytest
from battle_python.pathfinder import resolve_collisions
from battle_python.api_types import Coord, Battlesnake, Direction, GameState, Spam
from ..mocks.mock_api_types import get_mock_battlesnake, get_mock_gamestate


@pytest.mark.parametrize(
    "description, gs, expected",
    [
        (
            "Equal length snakes. Avoidable body collision and head collision",
            get_mock_gamestate(
                board_height=11,
                board_width=11,
                turn=0,
                food_coords=[(1, 1), (10, 10)],
                snakes=[
                    get_mock_battlesnake(
                        is_self=True,
                        id="Up -> Right",
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=0, y=8),
                        ],
                        health=100,
                    ),
                    get_mock_battlesnake(
                        id="Sidecar",
                        body_coords=[
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                        ],
                        health=100,
                    ),
                ],
            ),
            {
                "Up -> Right": {
                    Coord(x=1, y=10): Spam(
                        probability=100, direction="right", body_index=0
                    ),
                    Coord(x=0, y=10): Spam(probability=100, body_index=1),
                    Coord(x=0, y=9): Spam(probability=100, body_index=2),
                },
                "Sidecar": {
                    Coord(x=2, y=9): Spam(
                        probability=100, direction="right", body_index=0
                    ),
                    Coord(x=1, y=9): Spam(probability=100, body_index=1),
                    Coord(x=1, y=8): Spam(probability=100, body_index=2),
                },
            },
        ),
        (
            "Different length snakes. Avoidable body collision. Allow head collision",
            get_mock_gamestate(
                turn=0,
                snakes=[
                    get_mock_battlesnake(
                        is_self=True,
                        id="Up -> Right",
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=0, y=8),
                        ],
                        health=100,
                    ),
                    get_mock_battlesnake(
                        id="Sidecar",
                        body_coords=[
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                            Coord(x=1, y=6),
                        ],
                        health=100,
                    ),
                ],
            ),
            {
                "Up -> Right": {
                    Coord(x=1, y=10): Spam(
                        probability=100, direction="right", body_index=0
                    ),
                    Coord(x=0, y=10): Spam(probability=100, body_index=1),
                    Coord(x=0, y=9): Spam(probability=100, body_index=2),
                },
                "Sidecar": {
                    Coord(x=2, y=9): Spam(
                        probability=50, direction="right", body_index=0
                    ),
                    Coord(x=1, y=10): Spam(
                        probability=50, direction="up", body_index=0
                    ),
                    Coord(x=1, y=9): Spam(probability=100, body_index=1),
                    Coord(x=1, y=8): Spam(probability=100, body_index=2),
                    Coord(x=1, y=7): Spam(probability=100, body_index=3),
                },
            },
        ),
        (
            "A ménage à trois. Equal lengths",
            get_mock_gamestate(
                turn=0,
                snakes=[
                    get_mock_battlesnake(
                        is_self=True,
                        id="Up -> Right",
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=0, y=8),
                        ],
                        health=100,
                    ),
                    get_mock_battlesnake(
                        id="Sidecar",
                        body_coords=[
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                        ],
                        health=100,
                    ),
                    get_mock_battlesnake(
                        id="Up -> Left",
                        body_coords=[
                            Coord(x=2, y=10),
                            Coord(x=2, y=9),
                            Coord(x=2, y=8),
                        ],
                        health=100,
                    ),
                ],
            ),
            {
                "Up -> Right": {
                    Coord(x=1, y=10): Spam(
                        probability=100, direction="right", body_index=0
                    ),
                    Coord(x=0, y=10): Spam(probability=100, body_index=1),
                    Coord(x=0, y=9): Spam(probability=100, body_index=2),
                },
                "Sidecar": {
                    Coord(x=1, y=10): Spam(
                        probability=100, direction="up", body_index=0
                    ),
                    Coord(x=1, y=9): Spam(probability=100, body_index=1),
                    Coord(x=1, y=8): Spam(probability=100, body_index=2),
                },
                "Up -> Left": {
                    Coord(x=3, y=10): Spam(
                        probability=100, direction="right", body_index=0
                    ),
                    Coord(x=2, y=10): Spam(probability=100, body_index=1),
                    Coord(x=2, y=9): Spam(probability=100, body_index=2),
                },
            },
        ),
        (
            "A ménage à trois. Allow head collision",
            get_mock_gamestate(
                turn=0,
                snakes=[
                    get_mock_battlesnake(
                        is_self=True,
                        id="Up -> Right",
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=0, y=8),
                        ],
                        health=100,
                    ),
                    get_mock_battlesnake(
                        id="Sidecar",
                        body_coords=[
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                        ],
                        health=100,
                    ),
                    get_mock_battlesnake(
                        id="Up -> Left",
                        body_coords=[
                            Coord(x=2, y=10),
                            Coord(x=2, y=9),
                            Coord(x=2, y=8),
                            Coord(x=2, y=7),
                        ],
                        health=100,
                    ),
                ],
            ),
            {
                "Up -> Right": {
                    Coord(x=1, y=10): Spam(
                        probability=100, direction="right", body_index=0
                    ),
                    Coord(x=0, y=10): Spam(probability=100, body_index=1),
                    Coord(x=0, y=9): Spam(probability=100, body_index=2),
                },
                "Sidecar": {
                    Coord(x=1, y=10): Spam(
                        probability=100, direction="up", body_index=0
                    ),
                    Coord(x=1, y=9): Spam(probability=100, body_index=1),
                    Coord(x=1, y=8): Spam(probability=100, body_index=2),
                },
                "Up -> Left": {
                    Coord(x=1, y=10): Spam(
                        probability=50, direction="left", body_index=0
                    ),
                    Coord(x=3, y=10): Spam(
                        probability=50, direction="right", body_index=0
                    ),
                    Coord(x=2, y=10): Spam(probability=100, body_index=1),
                    Coord(x=2, y=9): Spam(probability=100, body_index=2),
                    Coord(x=2, y=8): Spam(probability=100, body_index=3),
                },
            },
        ),
        (
            "One snake. Three options",
            get_mock_gamestate(
                board_height=11,
                board_width=11,
                turn=0,
                food_coords=[(1, 1), (10, 10)],
                snakes=[
                    get_mock_battlesnake(
                        is_self=True,
                        id="Highlander",
                        body_coords=[
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                        ],
                        health=100,
                    ),
                ],
            ),
            {
                "Highlander": {
                    Coord(x=1, y=10): Spam(
                        probability=float(100 / 3), direction="up", body_index=0
                    ),
                    Coord(x=0, y=9): Spam(
                        probability=float(100 / 3), direction="left", body_index=0
                    ),
                    Coord(x=2, y=9): Spam(
                        probability=float(100 / 3), direction="right", body_index=0
                    ),
                    Coord(x=1, y=9): Spam(probability=100, body_index=1),
                    Coord(x=1, y=8): Spam(probability=100, body_index=2),
                },
            },
        ),
    ],
)
def test_resolve_collisions(
    description: str,
    gs: GameState,
    expected: dict[str, dict[Coord, Spam]],
):
    resolve_collisions(gs=gs, turn=gs.turn)
    for snake_id, expected_spam_dict in expected.items():
        spam_dict = gs.board.snake_dict[snake_id].turn_prob[gs.turn]
        assert spam_dict == expected_spam_dict
