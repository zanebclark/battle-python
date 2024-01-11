# def test_get_board_coords():
#     board_height = 11
#     board_width = 11
#
#     coords = get_board_coords(board_height=board_height, board_width=board_width)
#
#     for x in range(board_width):
#         for y in range(board_height):
#             assert Coord(x=x, y=y) in coords


# def test_rock_and_a_hard_place():
#     you = get_mock_battlesnake(
#         body_coords=[Coord(x=2, y=2), Coord(x=1, y=1), Coord(x=0, y=0)],
#         health=54,
#         latency=111,
#     )

#     gs = GameState(
#         game=get_mock_standard_game(),
#         turn=0,
#         board=get_mock_standard_board(
#             food_prob=[Coord(x=5, y=5), Coord(x=9, y=9), Coord(x=2, y=2)],
#             hazard_prob=[Coord(x=3, y=3)],
#             snakes=[
#                 you,
#                 get_mock_battlesnake(
#                     body_coords=[Coord(x=3, y=3), Coord(x=2, y=2), Coord(x=1, y=1), Coord(x=0, y=0)],
#                     health=16,
#                     latency=222,
#                 ),
#             ],
#         ),
#         you=you,
#     )

#     move = get_next_move(gs=gs)
#     assert move == "right"


# def test_upper_y_boundary():
#     you = get_mock_battlesnake(
#         body_coords=[Coord(x=0, y=0), Coord(x=0, y=0), Coord(x=0, y=0)],
#         health=54,
#         latency=111,
#     )

#     gs = GameState(
#         game=get_mock_standard_game(),
#         turn=0,
#         board=get_mock_standard_board(
#             food_prob=[Coord(x=5, y=5), Coord(x=9, y=9), Coord(x=2, y=2)],
#             hazard_prob=[Coord(x=3, y=3)],
#             snakes=[you],
#         ),
#         you=you,
#     )

#     move = get_next_move(gs=gs)
#     assert move == "right"


# def test_upper_x_boundary():
#     you = get_mock_battlesnake(
#         body_coords=[Coord(x=10, y=10), Coord(x=9, y=9), Coord(x=8, y=8)],
#         health=54,
#         latency=111,
#     )

#     gs = GameState(
#         game=get_mock_standard_game(),
#         turn=0,
#         board=get_mock_standard_board(
#             food_prob=[Coord(x=5, y=5), Coord(x=9, y=9), Coord(x=2, y=2)],
#             hazard_prob=[Coord(x=3, y=3)],
#             snakes=[you],
#         ),
#         you=you,
#     )

#     move = get_next_move(gs=gs)
#     assert move == "down"


# # def test_something_else():
# #     you = get_mock_battlesnake(
# #         body=[
# #             Coord(x=0, y=0),
# #             Coord(x=1, y=0),
# #             Coord(x=2, y=0),
# #         ],
# #         health=54,
# #         latency=111,
# #     )

# #     gs = GameState(
# #         game=get_mock_standard_game(),
# #         turn=0,
# #         board=get_mock_standard_board(
# #             food_prob=[Coord(x=5, y=5), Coord(x=9, y=9), Coord(x=2, y=2)],
# #             hazard_prob=[Coord(x=3, y=3)],
# #             snakes=[
# #                 you,
# #                 get_mock_battlesnake(
# #                     body=[
# #                         Coord(x=5, y=4),
# #                         Coord(x=5, y=3),
# #                         Coord(x=6, y=3),
# #                         Coord(x=6, y=2),
# #                     ],
# #                     health=16,
# #                     latency=222,
# #                 ),
# #             ],
# #         ),
# #         you=you,
# #     )

# #     spam(gs=gs)
