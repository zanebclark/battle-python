import pytest

from battle_python.BoardState import BoardState, DEATH_COORD
from battle_python.SnakeState import SnakeState, Elimination
from battle_python.api_types import Coord
from fixtures.timer import Timer
from mocks.get_mock_board_state import get_mock_board_state
from mocks.get_mock_snake_state import get_mock_snake_state


def test_board_state_get_flood_fill_coords():
    board = get_mock_board_state(
        my_snake=get_mock_snake_state(
            snake_id="C",
            body_coords=(Coord(x=9, y=7), Coord(x=9, y=8), Coord(x=9, y=9)),
        ),
        other_snakes=(
            get_mock_snake_state(
                snake_id="A",
                body_coords=(Coord(x=1, y=1), Coord(x=1, y=2), Coord(x=1, y=3)),
            ),
            get_mock_snake_state(
                snake_id="B",
                body_coords=(Coord(x=9, y=1), Coord(x=8, y=1), Coord(x=7, y=1)),
            ),
            get_mock_snake_state(
                snake_id="D",
                body_coords=(Coord(x=1, y=7), Coord(x=1, y=8), Coord(x=1, y=9)),
                health=100,
            ),
        ),
        food_coords=(
            Coord(x=3, y=1),
            Coord(x=2, y=5),
            Coord(x=8, y=3),
            Coord(x=5, y=5),
            Coord(x=10, y=7),
        ),
        board_height=11,
        board_width=11,
    )
    # with Timer():
    #     spam = board.get_flood_fill_coords(coord=board.my_snake.head, max_depth=10)

    with Timer():
        spam2 = board.spam()
        print(spam2)


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
        my_snake=get_mock_snake_state(
            snake_id="placeholder",
            body_coords=(DEATH_COORD,),
            is_self=True,
        ),
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
        ([Coord(x=1, y=1)], True),
        ([Coord(x=2, y=1)], False),
    ],
    ids=str,
)
def test_board_state_is_food_consumed(next_body: list[Coord], expected: bool):
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
                body_coords=(
                    DEATH_COORD,
                    Coord(x=0, y=10),
                    Coord(x=0, y=9),
                ),
                elimination=Elimination(cause="wall-collision"),
                health=86,
            ),
        ),
    ],
)
def test_board_state_get_next_snake_states_per_snake(
    snake: SnakeState,
    move: Coord,
    expected: SnakeState,
):
    board_state = get_mock_board_state(
        hazard_damage_rate=15,
        my_snake=snake,
        food_coords=(Coord(x=1, y=1),),
    )
    result = board_state.get_next_snake_state_for_snake_move(snake=snake, move=move)
    assert result.test_equals(expected) == True


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
def test_board_state_get_next_snake_states(
    snake_state: SnakeState,
    expected: list[SnakeState],
):
    board_state = get_mock_board_state(
        hazard_damage_rate=15,
        my_snake=snake_state,
        food_coords=(Coord(x=1, y=1),),
    )
    next_states = board_state.get_next_snake_states_for_snake(snake=snake_state)

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

        assert next_state.health == expected_state.health
        assert next_state.body == expected_state.body
        assert next_state.head == expected_state.head
        assert next_state.length == expected_state.length
        assert next_state.prev_state == board_state.my_snake


@pytest.mark.parametrize(
    "all_snakes, expected_snake_states, expected_food_coords",
    [
        (
            (
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
            ),
            (
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
            ),
            (Coord(x=0, y=10),),
        ),
        (
            (
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
            ),
            (
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
            ),
            tuple(),
        ),
        (
            (
                get_mock_snake_state(
                    snake_id="Shorter",
                    body_coords=(
                        Coord(x=1, y=10),
                        Coord(x=1, y=9),
                        Coord(x=1, y=8),
                    ),
                    is_self=True,
                ),
            ),
            (
                get_mock_snake_state(
                    snake_id="Shorter",
                    body_coords=(
                        Coord(x=1, y=10),
                        Coord(x=1, y=9),
                        Coord(x=1, y=8),
                    ),
                    is_self=True,
                    food_consumed=tuple(),
                ),
            ),
            (Coord(x=0, y=10),),
        ),
    ],
)
def test_board_state_model_post_init(
    all_snakes: tuple[SnakeState],
    expected_snake_states: tuple[SnakeState],
    expected_food_coords: tuple[Coord, ...],
):
    my_snake: SnakeState | None = None
    for snake in all_snakes:
        if snake.is_self:
            my_snake = snake

    if my_snake is None:
        raise Exception("My snake is not defined")

    other_snakes = tuple((snake for snake in all_snakes if not snake.is_self))
    board_state = get_mock_board_state(
        board_height=11,
        board_width=11,
        turn=0,
        my_snake=my_snake,
        other_snakes=other_snakes,
        food_coords=(Coord(x=0, y=10),),
    )
    assert board_state.food_coords == expected_food_coords
    for snake_state in all_snakes:
        expected_snake_state = None
        for some_snake_state in expected_snake_states:
            if snake_state.id == some_snake_state.id:
                expected_snake_state = some_snake_state
                break
        if expected_snake_state is None:
            raise Exception()
        assert snake_state.test_equals(expected_snake_state)


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
                        elimination=Elimination(
                            cause="head-collision", by="Up -> Right"
                        ),
                        murder_count=0,
                        health=21,
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
                        get_mock_snake_state(
                            snake_id="Up -> Left",
                            body_coords=(
                                Coord(x=3, y=10),
                                Coord(x=2, y=10),
                                Coord(x=2, y=9),
                            ),
                            murder_count=0,
                            health=21,
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
                        get_mock_snake_state(
                            snake_id="Up -> Left",
                            body_coords=(
                                Coord(x=1, y=10),
                                Coord(x=2, y=10),
                                Coord(x=2, y=9),
                            ),
                            elimination=Elimination(
                                cause="head-collision", by="Sidecar"
                            ),
                            murder_count=0,
                            health=21,
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
):
    board.populate_next_boards()
    for next_board in board.next_boards:
        expected_board = None
        for some_board in expected_boards:
            if next_board.get_other_key() == some_board.get_other_key():
                expected_board = some_board

        if expected_board is None:
            raise Exception()

        assert next_board.turn == expected_board.turn
        assert next_board.board_height == expected_board.board_height
        assert next_board.board_width == expected_board.board_width
        assert sorted(next_board.food_coords) == sorted(expected_board.food_coords)
        assert sorted(next_board.hazard_coords) == sorted(expected_board.hazard_coords)

        assert next_board.my_snake.health == expected_board.my_snake.health
        assert next_board.my_snake.body == expected_board.my_snake.body
        assert next_board.my_snake.head == expected_board.my_snake.head
        assert next_board.my_snake.length == expected_board.my_snake.length
        assert next_board.my_snake.elimination == expected_board.my_snake.elimination
        assert next_board.my_snake.murder_count == expected_board.my_snake.murder_count

        assert len(next_board.other_snakes) == len(expected_board.other_snakes)
        for snake_state in next_board.other_snakes:
            expected_state: SnakeState | None = None
            for some_expected_state in expected_board.other_snakes:
                if some_expected_state.id == snake_state.id:
                    expected_state = some_expected_state
                    break

            if expected_state is None:
                raise Exception()

            assert snake_state.health == expected_state.health
            assert snake_state.body == expected_state.body
            assert snake_state.head == expected_state.head
            assert snake_state.length == expected_state.length
            assert snake_state.elimination == expected_state.elimination
            assert snake_state.murder_count == expected_state.murder_count
