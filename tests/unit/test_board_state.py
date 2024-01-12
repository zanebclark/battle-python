import pytest

from battle_python.BoardState import BoardState
from battle_python.SnakeState import SnakeState
from battle_python.api_types import Coord
from mocks.get_mock_board_state import get_mock_board_state
from mocks.get_mock_snake_state import get_mock_snake_state


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
    ids=str,
)
def test_board_state_get_legal_adjacent_coords(coord: Coord, expected: list[Coord]):
    board = get_mock_board_state(
        board_height=11,
        board_width=11,
    )
    legal_adjacent_coords = board.get_legal_adjacent_coords(coord=coord)
    assert sorted(legal_adjacent_coords) == sorted(expected)


@pytest.mark.parametrize(
    "current_body, expected",
    [
        (
            [Coord(x=1, y=1), Coord(x=1, y=2), Coord(x=1, y=3)],
            [Coord(x=1, y=1), Coord(x=1, y=2), Coord(x=1, y=3), Coord(x=1, y=3)],
        ),
        (
            [Coord(x=2, y=1), Coord(x=2, y=2), Coord(x=2, y=3)],
            [Coord(x=2, y=1), Coord(x=2, y=2), Coord(x=2, y=3)],
        ),
    ],
    ids=str,
)
def test_board_state_get_next_body(current_body: list[Coord], expected: list[Coord]):
    board_state = get_mock_board_state(food_coords=[Coord(x=1, y=1)])
    next_body = board_state.get_next_body(current_body=current_body)
    assert next_body == expected


@pytest.mark.parametrize(
    "next_body, expected",
    [
        ([Coord(x=1, y=1)], True),
        ([Coord(x=2, y=1)], False),
    ],
    ids=str,
)
def test_board_state_is_food_consumed(next_body: list[Coord], expected: bool):
    board_state = get_mock_board_state(
        hazard_damage_rate=15,
        snake_states=[
            get_mock_snake_state(
                body_coords=[Coord(x=1000, y=1000)],
            )
        ],
        food_coords=[Coord(x=1, y=1)],
    )
    food_consumed = board_state.is_food_consumed(next_body=next_body)
    assert expected == food_consumed


@pytest.mark.parametrize(
    "next_body, food_consumed, health, expected_health",
    [
        ([Coord(x=1, y=1)], True, 50, 100),
        ([Coord(x=2, y=1)], False, 50, 34),
        ([Coord(x=3, y=1)], False, 50, 49),
        ([Coord(x=2, y=1)], False, 10, 0),
        ([Coord(x=2, y=1)], True, 200, 100),
    ],
    ids=str,
)
def test_board_state_get_next_health(
    next_body: list[Coord],
    food_consumed: bool,
    health: int,
    expected_health: int,
):
    board_state = get_mock_board_state(
        hazard_damage_rate=15,
        snake_states=[
            get_mock_snake_state(
                body_coords=[Coord(x=1000, y=1000)],
                health=health,
            )
        ],
        hazard_coords=[Coord(x=1, y=1), Coord(x=2, y=1)],
    )
    next_health = board_state.get_next_health(
        next_body=next_body,
        food_consumed=food_consumed,
        snake=board_state.snake_states[0],
    )
    assert next_health == expected_health


@pytest.mark.parametrize(
    "board, expected",
    [
        (
            get_mock_board_state(
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
            {
                "Left Border: Up -> Right": [
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
                ]
            },
        ),
        (
            get_mock_board_state(
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
            {
                "Left Border: Down -> Right": [
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
                ]
            },
        ),
        (
            get_mock_board_state(
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
            {
                "Right Border: Up -> Left": [
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
                ]
            },
        ),
        (
            get_mock_board_state(
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
            {
                "Right Border: Down -> Left": [
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
                ]
            },
        ),
        (
            get_mock_board_state(
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
            {
                "Bottom Border: Left -> Up": [
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
                ]
            },
        ),
        (
            get_mock_board_state(
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
            {
                "Bottom Border: Right -> Up": [
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
                ]
            },
        ),
        (
            get_mock_board_state(
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
            {
                "Top Border: Left -> Down": [
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
                ]
            },
        ),
        (
            get_mock_board_state(
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
            {
                "TopBorder:  Right -> Down": [
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
                ]
            },
        ),
        (
            get_mock_board_state(
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
            {
                "Two Options": [
                    get_mock_snake_state(
                        snake_id="Two Options",
                        is_self=True,
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
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=1, y=10),
                            Coord(x=2, y=10),
                        ],
                        health=99,
                    ),
                ]
            },
        ),
        (
            get_mock_board_state(
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
            {
                "Three Options": [
                    get_mock_snake_state(
                        snake_id="Three Options",
                        is_self=True,
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
                        body_coords=[
                            Coord(x=1, y=10),
                            Coord(x=1, y=9),
                            Coord(x=2, y=9),
                        ],
                        health=99,
                    ),
                ]
            },
        ),
        (
            get_mock_board_state(
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
            {
                "Ouroboros": [
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
                ]
            },
        ),
    ],
)
def test_board_state_get_next_snake_states_per_snake(
    board: BoardState,
    expected: dict[str, list[SnakeState]],
):
    snake: SnakeState | None = None
    for potential_snake in board.snake_states:
        if potential_snake.is_self:
            snake = potential_snake
            break

    if snake is None:
        raise Exception()

    next_states = board.get_next_snake_states_per_snake()

    assert len(next_states) == len(expected)
    for snake_id, next_states in next_states.items():
        for next_state in next_states:
            expected_state: SnakeState | None = None
            for some_expected_state in expected[snake_id]:
                if (
                    some_expected_state.snake_id == next_state.snake_id
                    and some_expected_state.body == next_state.body
                ):
                    expected_state = some_expected_state
                    break

            if expected_state is None:
                raise Exception()

            assert next_state.health == expected_state.health
            assert next_state.body == expected_state.body
            assert next_state.head == expected_state.head
            assert next_state.length == expected_state.length
            assert next_state.prev_state == snake


@pytest.mark.parametrize(
    "snake_states, expected",
    [
        (
            [
                get_mock_snake_state(
                    snake_id="Equal - 1",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ],
                    is_eliminated=False,
                    murder_count=0,
                ),
                get_mock_snake_state(
                    snake_id="Equal - 2",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                    ],
                    is_eliminated=False,
                    murder_count=0,
                ),
            ],
            [
                get_mock_snake_state(
                    snake_id="Equal - 1",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ],
                    is_eliminated=True,
                    murder_count=0,
                ),
                get_mock_snake_state(
                    snake_id="Equal - 2",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                    ],
                    is_eliminated=True,
                    murder_count=0,
                ),
            ],
        ),
        (
            [
                get_mock_snake_state(
                    snake_id="Shorter",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ],
                    is_eliminated=False,
                    murder_count=0,
                ),
                get_mock_snake_state(
                    snake_id="Longer",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                        Coord(x=3, y=10),
                    ],
                    is_eliminated=False,
                    murder_count=0,
                ),
            ],
            [
                get_mock_snake_state(
                    snake_id="Shorter",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ],
                    is_eliminated=True,
                    murder_count=0,
                ),
                get_mock_snake_state(
                    snake_id="Longer",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                        Coord(x=3, y=10),
                    ],
                    is_eliminated=False,
                    murder_count=1,
                ),
            ],
        ),
    ],
)
def test_board_state_resolve_head_collision(
    snake_states: list[SnakeState],
    expected: list[SnakeState],
):
    BoardState.resolve_head_collision(snake_heads_at_coord=snake_states)
    for snake_state in snake_states:
        expected_snake_state = None
        for some_snake_state in expected:
            if snake_state.snake_id == some_snake_state.snake_id:
                expected_snake_state = some_snake_state
                break
        if expected_snake_state is None:
            raise Exception()

        assert snake_state == expected_snake_state


@pytest.mark.parametrize(
    "snake_states, expected_snake_states, expected_food_coords",
    [
        (
            [
                get_mock_snake_state(
                    snake_id="Equal - 1",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ],
                    food_consumed=[],
                    is_eliminated=True,
                ),
                get_mock_snake_state(
                    snake_id="Equal - 2",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                    ],
                    food_consumed=[],
                    is_eliminated=True,
                ),
            ],
            [
                get_mock_snake_state(
                    snake_id="Equal - 1",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ],
                    food_consumed=[],
                    is_eliminated=True,
                ),
                get_mock_snake_state(
                    snake_id="Equal - 2",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                    ],
                    food_consumed=[],
                    is_eliminated=True,
                ),
            ],
            [Coord(x=0, y=10)],
        ),
        (
            [
                get_mock_snake_state(
                    snake_id="Shorter",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ],
                    food_consumed=[],
                    is_eliminated=True,
                ),
                get_mock_snake_state(
                    snake_id="Longer",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                        Coord(x=3, y=10),
                    ],
                    food_consumed=[],
                    is_eliminated=False,
                ),
            ],
            [
                get_mock_snake_state(
                    snake_id="Shorter",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=0, y=9),
                        Coord(x=0, y=8),
                    ],
                    food_consumed=[],
                    is_eliminated=True,
                ),
                get_mock_snake_state(
                    snake_id="Longer",
                    body_coords=[
                        Coord(x=0, y=10),
                        Coord(x=1, y=10),
                        Coord(x=2, y=10),
                        Coord(x=3, y=10),
                    ],
                    food_consumed=[Coord(x=0, y=10)],
                    is_eliminated=False,
                ),
            ],
            [],
        ),
        (
            [
                get_mock_snake_state(
                    snake_id="Shorter",
                    body_coords=[
                        Coord(x=1, y=10),
                        Coord(x=1, y=9),
                        Coord(x=1, y=8),
                    ],
                    food_consumed=[],
                )
            ],
            [
                get_mock_snake_state(
                    snake_id="Shorter",
                    body_coords=[
                        Coord(x=1, y=10),
                        Coord(x=1, y=9),
                        Coord(x=1, y=8),
                    ],
                    food_consumed=[],
                )
            ],
            [Coord(x=0, y=10)],
        ),
    ],
)
def test_board_state_resolve_food_consumption(
    snake_states: list[SnakeState],
    expected_snake_states: list[SnakeState],
    expected_food_coords: list[Coord],
):
    board_state = get_mock_board_state(
        board_height=11,
        board_width=11,
        turn=0,
        snake_states=snake_states,
        food_coords=[Coord(x=0, y=10)],
    )
    board_state.resolve_food_consumption(
        coord=board_state.snake_states[0].head, snake_heads_at_coord=snake_states
    )
    assert board_state.food_coords == expected_food_coords
    for snake_state in snake_states:
        expected_snake_state = None
        for some_snake_state in expected_snake_states:
            if snake_state.snake_id == some_snake_state.snake_id:
                expected_snake_state = some_snake_state
                break
        if expected_snake_state is None:
            raise Exception()

        assert snake_state == expected_snake_state


@pytest.mark.parametrize(
    "description, board, expected_boards",
    [
        (
            "Equal length snakes. Avoidable body collision and head collision",
            get_mock_board_state(
                board_height=11,
                board_width=11,
                turn=0,
                snake_states=[
                    get_mock_snake_state(
                        is_self=True,
                        snake_id="Up -> Right",
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=0, y=8),
                        ],
                        is_eliminated=False,
                        murder_count=0,
                        health=89,
                    ),
                    get_mock_snake_state(
                        snake_id="Sidecar",
                        body_coords=[
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                        ],
                        is_eliminated=False,
                        murder_count=0,
                        health=64,
                    ),
                ],
            ),
            [
                get_mock_board_state(
                    board_height=11,
                    board_width=11,
                    turn=1,
                    snake_states=[
                        get_mock_snake_state(
                            is_self=True,
                            snake_id="Up -> Right",
                            body_coords=[
                                Coord(x=1, y=10),
                                Coord(x=0, y=10),
                                Coord(x=0, y=9),
                            ],
                            is_eliminated=True,
                            murder_count=0,
                            health=88,
                        ),
                        get_mock_snake_state(
                            snake_id="Sidecar",
                            body_coords=[
                                Coord(x=1, y=10),
                                Coord(x=1, y=9),
                                Coord(x=1, y=8),
                            ],
                            is_eliminated=True,
                            murder_count=0,
                            health=63,
                        ),
                    ],
                ),
                get_mock_board_state(
                    board_height=11,
                    board_width=11,
                    turn=1,
                    snake_states=[
                        get_mock_snake_state(
                            is_self=True,
                            snake_id="Up -> Right",
                            body_coords=[
                                Coord(x=1, y=10),
                                Coord(x=0, y=10),
                                Coord(x=0, y=9),
                            ],
                            is_eliminated=False,
                            murder_count=0,
                            health=88,
                        ),
                        get_mock_snake_state(
                            snake_id="Sidecar",
                            body_coords=[
                                Coord(x=2, y=9),
                                Coord(x=1, y=9),
                                Coord(x=1, y=8),
                            ],
                            is_eliminated=False,
                            murder_count=0,
                            health=63,
                        ),
                    ],
                ),
            ],
        ),
        (
            "Different length snakes. Avoidable body collision. Allow head collision",
            get_mock_board_state(
                board_height=11,
                board_width=11,
                turn=0,
                snake_states=[
                    get_mock_snake_state(
                        is_self=True,
                        snake_id="Up -> Right",
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=0, y=8),
                        ],
                        is_eliminated=False,
                        murder_count=0,
                        health=89,
                    ),
                    get_mock_snake_state(
                        snake_id="Sidecar",
                        body_coords=[
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                            Coord(x=1, y=6),
                        ],
                        is_eliminated=False,
                        murder_count=0,
                        health=64,
                    ),
                ],
            ),
            [
                get_mock_board_state(
                    board_height=11,
                    board_width=11,
                    turn=1,
                    snake_states=[
                        get_mock_snake_state(
                            is_self=True,
                            snake_id="Up -> Right",
                            body_coords=[
                                Coord(x=1, y=10),
                                Coord(x=0, y=10),
                                Coord(x=0, y=9),
                            ],
                            is_eliminated=True,
                            murder_count=0,
                            health=88,
                        ),
                        get_mock_snake_state(
                            snake_id="Sidecar",
                            body_coords=[
                                Coord(x=1, y=10),
                                Coord(x=1, y=9),
                                Coord(x=1, y=8),
                                Coord(x=1, y=7),
                            ],
                            is_eliminated=False,
                            murder_count=1,
                            health=63,
                        ),
                    ],
                ),
                get_mock_board_state(
                    board_height=11,
                    board_width=11,
                    turn=1,
                    snake_states=[
                        get_mock_snake_state(
                            is_self=True,
                            snake_id="Up -> Right",
                            body_coords=[
                                Coord(x=1, y=10),
                                Coord(x=0, y=10),
                                Coord(x=0, y=9),
                            ],
                            is_eliminated=False,
                            murder_count=0,
                            health=88,
                        ),
                        get_mock_snake_state(
                            snake_id="Sidecar",
                            body_coords=[
                                Coord(x=2, y=9),
                                Coord(x=1, y=9),
                                Coord(x=1, y=8),
                                Coord(x=1, y=7),
                            ],
                            is_eliminated=False,
                            murder_count=0,
                            health=63,
                        ),
                    ],
                ),
            ],
        ),
        (
            "A ménage à trois. Equal lengths",
            get_mock_board_state(
                board_height=11,
                board_width=11,
                turn=0,
                snake_states=[
                    get_mock_snake_state(
                        is_self=True,
                        snake_id="Up -> Right",
                        body_coords=[
                            Coord(x=0, y=10),
                            Coord(x=0, y=9),
                            Coord(x=0, y=8),
                        ],
                        is_eliminated=False,
                        murder_count=0,
                        health=89,
                    ),
                    get_mock_snake_state(
                        snake_id="Sidecar",
                        body_coords=[
                            Coord(x=1, y=9),
                            Coord(x=1, y=8),
                            Coord(x=1, y=7),
                        ],
                        is_eliminated=False,
                        murder_count=0,
                        health=64,
                    ),
                    get_mock_snake_state(
                        snake_id="Up -> Left",
                        body_coords=[
                            Coord(x=2, y=10),
                            Coord(x=2, y=9),
                            Coord(x=2, y=8),
                        ],
                        is_eliminated=False,
                        murder_count=0,
                        health=22,
                    ),
                ],
            ),
            [
                get_mock_board_state(
                    board_height=11,
                    board_width=11,
                    turn=1,
                    snake_states=[
                        get_mock_snake_state(
                            is_self=True,
                            snake_id="Up -> Right",
                            body_coords=[
                                Coord(x=1, y=10),
                                Coord(x=0, y=10),
                                Coord(x=0, y=9),
                            ],
                            is_eliminated=True,
                            murder_count=0,
                            health=88,
                        ),
                        get_mock_snake_state(
                            snake_id="Sidecar",
                            body_coords=[
                                Coord(x=1, y=10),
                                Coord(x=1, y=9),
                                Coord(x=1, y=8),
                            ],
                            is_eliminated=True,
                            murder_count=0,
                            health=63,
                        ),
                        get_mock_snake_state(
                            snake_id="Up -> Left",
                            body_coords=[
                                Coord(x=1, y=10),
                                Coord(x=2, y=10),
                                Coord(x=2, y=9),
                            ],
                            is_eliminated=True,
                            murder_count=0,
                            health=21,
                        ),
                    ],
                ),
                get_mock_board_state(
                    board_height=11,
                    board_width=11,
                    turn=1,
                    snake_states=[
                        get_mock_snake_state(
                            is_self=True,
                            snake_id="Up -> Right",
                            body_coords=[
                                Coord(x=1, y=10),
                                Coord(x=0, y=10),
                                Coord(x=0, y=9),
                            ],
                            is_eliminated=True,
                            murder_count=0,
                            health=88,
                        ),
                        get_mock_snake_state(
                            snake_id="Sidecar",
                            body_coords=[
                                Coord(x=1, y=10),
                                Coord(x=1, y=9),
                                Coord(x=1, y=8),
                            ],
                            is_eliminated=True,
                            murder_count=0,
                            health=63,
                        ),
                        get_mock_snake_state(
                            snake_id="Up -> Left",
                            body_coords=[
                                Coord(x=3, y=10),
                                Coord(x=2, y=10),
                                Coord(x=2, y=9),
                            ],
                            is_eliminated=False,
                            murder_count=0,
                            health=21,
                        ),
                    ],
                ),
                get_mock_board_state(
                    board_height=11,
                    board_width=11,
                    turn=1,
                    snake_states=[
                        get_mock_snake_state(
                            is_self=True,
                            snake_id="Up -> Right",
                            body_coords=[
                                Coord(x=1, y=10),
                                Coord(x=0, y=10),
                                Coord(x=0, y=9),
                            ],
                            is_eliminated=False,
                            murder_count=0,
                            health=88,
                        ),
                        get_mock_snake_state(
                            snake_id="Sidecar",
                            body_coords=[
                                Coord(x=2, y=9),
                                Coord(x=1, y=9),
                                Coord(x=1, y=8),
                            ],
                            is_eliminated=False,
                            murder_count=0,
                            health=63,
                        ),
                        get_mock_snake_state(
                            snake_id="Up -> Left",
                            body_coords=[
                                Coord(x=3, y=10),
                                Coord(x=2, y=10),
                                Coord(x=2, y=9),
                            ],
                            is_eliminated=False,
                            murder_count=0,
                            health=21,
                        ),
                    ],
                ),
                get_mock_board_state(
                    board_height=11,
                    board_width=11,
                    turn=1,
                    snake_states=[
                        get_mock_snake_state(
                            is_self=True,
                            snake_id="Up -> Right",
                            body_coords=[
                                Coord(x=1, y=10),
                                Coord(x=0, y=10),
                                Coord(x=0, y=9),
                            ],
                            is_eliminated=False,
                            murder_count=0,
                            health=88,
                        ),
                        get_mock_snake_state(
                            snake_id="Sidecar",
                            body_coords=[
                                Coord(x=2, y=9),
                                Coord(x=1, y=9),
                                Coord(x=1, y=8),
                            ],
                            is_eliminated=False,
                            murder_count=0,
                            health=63,
                        ),
                        get_mock_snake_state(
                            snake_id="Up -> Left",
                            body_coords=[
                                Coord(x=1, y=10),
                                Coord(x=2, y=10),
                                Coord(x=2, y=9),
                            ],
                            is_eliminated=True,
                            murder_count=0,
                            health=21,
                        ),
                    ],
                ),
            ],
        ),
    ],
)
def test_board_state_get_next_boards(
    description: str,
    board: BoardState,
    expected_boards: list[BoardState],
):
    next_boards = board.get_next_boards()
    for next_board in next_boards:
        expected_board = None
        next_board_sort_key = sorted(
            [
                coord
                for snake_state in next_board.snake_states
                for coord in snake_state.body
            ]
        )
        for some_board in expected_boards:
            some_board_sort_key = sorted(
                [
                    coord
                    for snake_state in some_board.snake_states
                    for coord in snake_state.body
                ]
            )
            if some_board_sort_key == next_board_sort_key:
                expected_board = some_board

        if expected_board is None:
            raise Exception()

        assert next_board.turn == expected_board.turn
        assert next_board.board_height == expected_board.board_height
        assert next_board.board_width == expected_board.board_width
        assert sorted(next_board.food_coords) == sorted(expected_board.food_coords)
        assert sorted(next_board.hazard_coords) == sorted(expected_board.hazard_coords)
        assert len(next_board.snake_states) == len(expected_board.snake_states)
        for snake_state in next_board.snake_states:
            expected_state: SnakeState | None = None
            for some_expected_state in expected_board.snake_states:
                if some_expected_state.snake_id == snake_state.snake_id:
                    expected_state = some_expected_state
                    break

            if expected_state is None:
                raise Exception()

            assert snake_state.health == expected_state.health
            assert snake_state.body == expected_state.body
            assert snake_state.head == expected_state.head
            assert snake_state.length == expected_state.length
            assert snake_state.is_eliminated == expected_state.is_eliminated
            assert snake_state.murder_count == expected_state.murder_count
