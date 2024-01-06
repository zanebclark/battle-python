from dataclasses import dataclass

from battle_python.api_types import (
    Coord,
    Direction,
    Battlesnake,
    GameState,
)


# The tail might not be there. If the snake just ate food (health = 100), it will remain.
# The snake's health will be at 100 at the beginning of the game, so omit that condition.
def is_snake_growing(turn: int, health: int) -> bool:
    if turn == 0:
        return False
    return health == 100


def get_body_evading_moves(
    body_coords: list[Coord],
    snake_growing: bool,
    board_width: int,
    board_height: int,
) -> dict[Coord, Direction]:
    moves = body_coords[0].get_legal_moves(
        board_width=board_width, board_height=board_height
    )

    for coord in list(moves.keys()):
        if coord in body_coords[0:-1]:  # Avoid self collision.
            del moves[coord]
            continue

        # Avoid your tail if it won't move
        if coord == body_coords[-1] and snake_growing:
            del moves[coord]
            continue

    return moves


@dataclass
class Spam:
    probability: float
    body_index: int = None
    direction: Direction | None = None


def get_coord_prob_dict(
    state_prob: float,
    body_coords: list[Coord],
    health: int,
    turn: int,
    board_width: int,
    board_height: int,
) -> dict[Coord, Spam]:
    coord_prob_dict: dict[Coord, Spam] = {}

    snake_growing = is_snake_growing(turn=turn, health=health)

    for current_body_index, coord in enumerate(body_coords):
        body_index = current_body_index + 1
        if coord == body_coords[-1] and not snake_growing:
            continue

        coord_prob_dict[coord] = Spam(probability=state_prob, body_index=body_index)

    safe_moves = get_body_evading_moves(
        body_coords=body_coords,
        snake_growing=snake_growing,
        board_width=board_width,
        board_height=board_height,
    )
    options = float(len(safe_moves.keys()))
    if options == 0:
        return coord_prob_dict
    prob = state_prob / float(len(safe_moves.keys()))
    for coord, direction in safe_moves.items():
        if coord_prob_dict.get(coord) is None:
            coord_prob_dict[coord] = Spam(
                probability=prob, body_index=0, direction=direction
            )
        else:
            # Ouroboros
            coord_prob_dict[coord].probability += prob

    return coord_prob_dict


#
# def get_combined_coord_prob_dict(
#     gs: GameState,
# ) -> dict[Coord, dict[str, Spam]]:
#     spam: dict[Coord, dict[str, Spam]] = {}
#
#     snake_dict: dict[str, Battlesnake] = {
#         snake.id: snake for snake in snakes
#     }  # TODO: persist this somewhere for the turn in question
#
#     # Since food restores the health this turn and causes the snake to grow the next turn,
#     # I don't have to consider food on this level.
#     for snake in snakes:
#         coord_prob_dict = get_coord_prob_dict(
#             state_prob=100,
#             body_coords=snake.body,
#             health=snake.health,
#             turn=turn,
#             board_width=board_width,
#             board_height=board_height,
#         )
#
#         for coord, direction in coord_prob_dict.items():
#             if spam.get(coord) is None:
#                 spam[coord] = {}
#             spam[coord][snake.id] = direction
#     print("Hey there!")
#     # for coord, spam_dict in spam.items():
#     #     # Multiple snake bodies can't exist in the same square in the standard game mode
#     #     # This condition reflects:
#     #     # - A snake body and a potential snake move
#     #     # - Two potential snake moves
#     #     if len(spam_dict.keys()) > 1:
#     #         for snake_id in list(spam_dict.keys()):
#     #             delete_spam_inst = False
#     #             spam_inst = spam_dict[snake_id]
#     #             # A body collision
#     #             if spam_inst.body_index > 0:
#     #                 delete_spam_inst = True
#     #
#     #             # A head-to-head-collision
#     #             else:
#     #                 snake_dict[snake_id]
#     #
#     #
#     #             if delete_spam_inst:
#     #                 pass
#     #                 # del spam_dict[snake_id]
#     #                 # TODO: How do I recalculate the new potentials?
#     #
#     #
#     #             # snake_dict[snake_id]
