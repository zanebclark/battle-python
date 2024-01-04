from typing import List, Tuple
import pytest
from battle_python.BattlesnakeTypes import Coord, GameState
from tests.mocks.MockBattlesnakeTypes import (
    get_mock_battlesnake,
    get_mock_standard_board,
    get_mock_standard_game,
)


def test_game_state():
    you = get_mock_battlesnake(
        body_coords=[(2, 0), (1, 0), (0, 0)],
        health=54,
        latency=111,
    )

    board_height = 70
    board_width = 50
    turn = 11

    gs = GameState(
        game=get_mock_standard_game(),
        turn=turn,
        board=get_mock_standard_board(
            width=board_width,
            height=board_height,
            food_coords=[(5, 5), (9, 0), (2, 6)],
            hazard_coords=[(3, 2)],
            snakes=[
                you,
                get_mock_battlesnake(
                    body_coords=[(3, 1), (2, 1), (1, 1), (0, 1)],
                    health=16,
                    latency=222,
                ),
            ],
        ),
        you=you,
    )
    for snake in gs.board.snakes:
        assert snake.board_height == board_height
        assert snake.board_width == board_width
        assert snake.turn == turn
        if snake.id != you.id:
            assert not snake.is_self
        else:
            assert snake.is_self


@pytest.mark.parametrize(
    "health, turn, expected",
    [
        (100, 0, True),
        (100, 1, False),
        (88, 0, True),
        (88, 1, True),
    ],
)
def test_battlesnake_tail_will_move(health: int, turn: int, expected: bool):
    snake = get_mock_battlesnake(
        body_coords=[(3, 1), (2, 1)],
        health=health,
        turn=turn,
    )
    assert snake.tail_will_move() is expected


def test_battlesnake_get_moves():
    head_x = 5
    head_y = 1

    snake = get_mock_battlesnake(body_coords=[(head_x, head_y)])
    moves = snake.get_moves()

    assert moves[Coord(head_x, head_y + 1)] == "up"
    assert moves[Coord(head_x, head_y - 1)] == "down"
    assert moves[Coord(head_x - 1, head_y)] == "left"
    assert moves[Coord(head_x + 1, head_y)] == "right"


@pytest.mark.parametrize(
    "body_coords, health, turn, expected",
    [
        # # Left Border
        # ([(0, 10), (0, 9), (0, 8)], 100, 0, [Coord(x=1, y=10)]),  # Up -> Right
        # ([(0, 0), (0, 1), (0, 2)], 100, 0, [Coord(x=1, y=0)]),  # Down -> Right
        # # Right Border
        # ([(10, 10), (10, 9), (10, 8)], 100, 0, [Coord(x=9, y=10)]),  # Up -> Left
        # ([(10, 0), (10, 1), (10, 2)], 100, 0, [Coord(x=9, y=0)]),  # Down -> Left
        # # Bottom Border
        # ([(0, 0), (1, 0), (2, 0)], 100, 0, [Coord(x=0, y=1)]),  # Left -> Up
        # ([(10, 0), (9, 0), (8, 0)], 100, 0, [Coord(x=10, y=1)]),  # Right -> Up
        # # Top Border
        # ([(0, 10), (1, 10), (2, 10)], 100, 0, [Coord(x=0, y=9)]),  # Left -> Down
        # ([(10, 10), (9, 10), (8, 10)], 100, 0, [Coord(x=10, y=9)]),  # Right -> Down
        # Two Options
        ([(1, 10), (2, 10)], 100, 0, [Coord(x=0, y=10), Coord(x=1, y=9)]),
        # Three Options
        (
            [(1, 9), (2, 9)],
            100,
            0,
            [Coord(x=1, y=10), Coord(x=0, y=9), Coord(x=1, y=8)],
        ),
        # Ouroboros
        (
            [(0, 10), (0, 9), (1, 9), (1, 10)],
            90,
            5,
            [Coord(x=1, y=10)],
        ),
    ],
)
def test_battlesnake_get_safe_moves(
    body_coords: List[Tuple[int, int]], health: int, turn: int, expected: List[Coord]
):
    board_width = 11
    board_height = 11
    snake = get_mock_battlesnake(
        board_width=board_width,
        board_height=board_height,
        turn=turn,
        body_coords=body_coords,
        health=health,
    )
    moves = snake.get_safe_moves()

    assert len(moves.keys()) == len(expected)
    for move in moves.keys():
        assert move in expected
