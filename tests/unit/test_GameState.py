import pytest
from battle_python.GameState import GameState
from battle_python.types import Coord, get_board_coords
from tests.mocks.MockBattlesnakeTypes import (
    get_mock_battlesnake,
    get_mock_standard_board,
    get_mock_standard_game,
)


def test_get_board_coords():
    board_height = 11
    board_width = 11

    coords = get_board_coords(board_height=board_height, board_width=board_width)

    for x in range(board_width):
        for y in range(board_height):
            assert Coord(x=x, y=y) in coords


def test_game_state_init():
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

    assert len(gs.cells) == ((board_height) * (board_width))
