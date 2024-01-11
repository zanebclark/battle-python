from __future__ import annotations

from itertools import product

from battle_python.api_types import Coord


def get_board_coords(board_width: int, board_height: int) -> list[Coord]:
    coords: list[Coord] = [
        Coord(x=x, y=y) for x, y in product(range(board_width), range(board_height))
    ]
    return coords


# TODO: Don't persist the snake states, just the aggregate
# TODO: Oct tree google

# @dataclass
# class Game:
#     def next_frame(self):
#         # TODO: Has the food_prob been eaten?
#         # TODO: Where could the snakes move?
#         # TODO: Hazard progression?
#         current_frame = self.frames[-1]
#         for snake in current_frame.snakes:
#             safe_moves = current_frame.get_safe_moves(snake_head_coord=snake.head)
#             move_prob = round(100 / len(safe_moves.keys()))

#         # for snake in current_frame.snakes.values():

#         #     if

#         your_snake = current_frame.snakes[self.your_battlesnake_id]

#         # Append the last move
#         # your_snake.body.insert(0, move)

#         # If you ate food_prob on the previous round, your health will be at 100 and your tail won't be popped this round
#         if your_snake.health != 100:
#             your_snake.body.pop()

#         your_snake = None
#         for coord in self.coords:
#             pass
#         # self.frames.append(next_gs)


# def get_next_move(gs: GameState):
#     game = Game.from_game_state(gs=gs)
#     moves = game.frames[0].get_safe_moves(game.frames[0].you.head)

#     # TODO: Implement some sort of yield to return a move here

#     return random.choice(list(moves.values()))


# from battle_python.game_state import (
#     Coord,
#     Snake,
#     GameState,
#     get_coord_prob_dict,
#     Spam,
# )


# def resolve_body_collisions(
#     gs: GameState, turn: int, coord: Coord, spam_dict: dict[str, Spam]
# ) -> dict[str, Spam]:
#     if len(spam_dict.keys()) == 1:
#         return spam_dict
#     winner_ids = [
#         snake_id for snake_id, spam in spam_dict.items() if spam.body_index > 0
#     ]
#     if len(winner_ids) == 0:
#         return spam_dict
#     if len(winner_ids) > 1:
#         raise Exception(f"Two snakes are in the same space: {winner_ids}")
#     winner_id = winner_ids[0]
#
#     for loser_id in list(spam_dict.keys()):
#         if loser_id == winner_id:
#             continue
#         gs.board.snake_dict[loser_id].delete_from_turn_prob(turn=turn, coord=coord)
#         del spam_dict[loser_id]
#
#     return spam_dict


# def resolve_head_collisions(
#     gs: GameState, turn: int, coord: Coord, spam_dict: dict[str, Spam]
# ) -> dict[str, Spam]:
#     # Only head-to-head-collisions should remain
#     if len(spam_dict.keys()) <= 1:
#         return spam_dict
#
#     snake_lengths: dict[int, list[Snake]] = {}
#     for snake_id in list(spam_dict.keys()):
#         snake = gs.board.snake_dict[snake_id]
#         if snake_lengths.get(snake.length) is None:
#             snake_lengths[snake.length] = []
#         snake_lengths[snake.length].append(snake)
#
#     longest_length = sorted(list(snake_lengths.keys()))[-1]
#
#     if len(snake_lengths[longest_length]) > 1:
#         # Delete all of the snakes. # TODO: Validate this behavior. The little guy might win here
#         for snake_id in list(spam_dict.keys()):
#             gs.board.snake_dict[snake_id].delete_from_turn_prob(turn=turn, coord=coord)
#             del spam_dict[snake_id]
#
#     elif len(snake_lengths[longest_length]) == 1:
#         # There is a longer snake. Delete shorter snakes
#         for snake_id in list(spam_dict.keys()):
#             snake = gs.board.snake_dict[snake_id]
#             if snake.id == snake_lengths[longest_length][0].id:
#                 continue
#             snake.delete_from_turn_prob(turn=turn, coord=coord)
#             del spam_dict[snake.id]
#     else:
#         raise Exception(f"There isn't a longest snake?")
#
#     return spam_dict


# def resolve_collisions(gs: GameState, turn: int) -> None:
#     combined_coord_prob_dict: dict[Coord, dict[str, Spam]] = {}
#
#     for snake in gs.board.snake_dict.values():
#         coord_prob_dict = get_coord_prob_dict(
#             state_prob=100,
#             body_coords=snake.body,
#             health=snake.health,
#             turn=turn,
#             board_width=gs.board.width,
#             board_height=gs.board.height,
#         )
#         snake.turn_prob[turn] = coord_prob_dict
#
#         for coord, direction in coord_prob_dict.items():
#             if combined_coord_prob_dict.get(coord) is None:
#                 combined_coord_prob_dict[coord] = {}
#             combined_coord_prob_dict[coord][snake.id] = direction
#
#     # Multiple snake bodies can't exist in the same square in the standard game mode
#     # This condition reflects:
#     # - A snake body and a potential snake move or
#     # - Two potential snake moves
#     for coord in combined_coord_prob_dict.keys():
#         combined_coord_prob_dict[coord] = resolve_body_collisions(
#             gs=gs, turn=turn, coord=coord, spam_dict=combined_coord_prob_dict[coord]
#         )
#     for coord in combined_coord_prob_dict.keys():
#         combined_coord_prob_dict[coord] = resolve_head_collisions(
#             gs=gs, turn=turn, coord=coord, spam_dict=combined_coord_prob_dict[coord]
#         )
