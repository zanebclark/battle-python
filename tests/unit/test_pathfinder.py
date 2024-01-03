import pytest

from battle_python.BattlesnakeTypes import Coord, GameState
from battle_python.pathfinder import get_next_move
from tests.mocks.MockBattlesnakeTypes import (
    get_mock_battlesnake,
    get_mock_standard_board,
    get_mock_standard_game,
)


def test_rock_and_a_hard_place():
    you = get_mock_battlesnake(
        body=[
            Coord(x=2, y=0),
            Coord(x=1, y=0),
            Coord(x=0, y=0),
        ],
        health=54,
        latency=111,
    )

    gs = GameState(
        game=get_mock_standard_game(),
        turn=0,
        board=get_mock_standard_board(
            food_coords=[(5, 5), (9, 0), (2, 6)],
            hazard_coords=[(3, 2)],
            snakes=[
                you,
                get_mock_battlesnake(
                    body=[
                        Coord(x=3, y=1),
                        Coord(x=2, y=1),
                        Coord(x=1, y=1),
                        Coord(x=0, y=1),
                    ],
                    health=16,
                    latency=222,
                ),
            ],
        ),
        you=you,
    )

    move = get_next_move(gs=gs)
    assert move == "right"


def test_upper_y_boundry():
    you = get_mock_battlesnake(
        body=[
            Coord(x=0, y=10),
            Coord(x=0, y=9),
            Coord(x=0, y=8),
        ],
        health=54,
        latency=111,
    )

    gs = GameState(
        game=get_mock_standard_game(),
        turn=0,
        board=get_mock_standard_board(
            food_coords=[(5, 5), (9, 0), (2, 6)],
            hazard_coords=[(3, 2)],
            snakes=[you],
        ),
        you=you,
    )

    move = get_next_move(gs=gs)
    assert move == "right"


def test_upper_x_boundry():
    you = get_mock_battlesnake(
        body=[
            Coord(x=10, y=10),
            Coord(x=9, y=10),
            Coord(x=8, y=10),
        ],
        health=54,
        latency=111,
    )

    gs = GameState(
        game=get_mock_standard_game(),
        turn=0,
        board=get_mock_standard_board(
            food_coords=[(5, 5), (9, 0), (2, 6)],
            hazard_coords=[(3, 2)],
            snakes=[you],
        ),
        you=you,
    )

    move = get_next_move(gs=gs)
    assert move == "down"


# def test_something_else():
#     you = get_mock_battlesnake(
#         body=[
#             Coord(x=0, y=0),
#             Coord(x=1, y=0),
#             Coord(x=2, y=0),
#         ],
#         health=54,
#         latency=111,
#     )

#     gs = GameState(
#         game=get_mock_standard_game(),
#         turn=0,
#         board=get_mock_standard_board(
#             food_coords=[(5, 5), (9, 0), (2, 6)],
#             hazard_coords=[(3, 2)],
#             snakes=[
#                 you,
#                 get_mock_battlesnake(
#                     body=[
#                         Coord(x=5, y=4),
#                         Coord(x=5, y=3),
#                         Coord(x=6, y=3),
#                         Coord(x=6, y=2),
#                     ],
#                     health=16,
#                     latency=222,
#                 ),
#             ],
#         ),
#         you=you,
#     )

#     spam(gs=gs)
