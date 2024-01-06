from battle_python.api_types import (
    Coord,
    Battlesnake,
    GameState,
    get_coord_prob_dict,
    Spam,
)


def resolve_body_collisions(
    gs: GameState, turn: int, coord: Coord, spam_dict: dict[str, Spam]
) -> dict[str, Spam]:
    if len(spam_dict.keys()) == 1:
        return spam_dict
    winner_ids = [
        snake_id for snake_id, spam in spam_dict.items() if spam.body_index > 0
    ]
    if len(winner_ids) == 0:
        return spam_dict
    if len(winner_ids) > 1:
        raise Exception(f"Two snakes are in the same space: {winner_ids}")
    winner_id = winner_ids[0]

    for loser_id in list(spam_dict.keys()):
        if loser_id == winner_id:
            continue
        gs.board.snake_dict[loser_id].delete_from_turn_prob(turn=turn, coord=coord)
        del spam_dict[loser_id]

    return spam_dict


def resolve_head_collisions(
    gs: GameState, turn: int, coord: Coord, spam_dict: dict[str, Spam]
) -> dict[str, Spam]:
    # Only head-to-head-collisions should remain
    if len(spam_dict.keys()) <= 1:
        return spam_dict

    snake_lengths: dict[int, list[Battlesnake]] = {}
    for snake_id in list(spam_dict.keys()):
        snake = gs.board.snake_dict[snake_id]
        if snake_lengths.get(snake.length) is None:
            snake_lengths[snake.length] = []
        snake_lengths[snake.length].append(snake)

    longest_length = sorted(list(snake_lengths.keys()))[-1]

    if len(snake_lengths[longest_length]) > 1:
        # Delete all of the snakes. # TODO: Validate this behavior. The little guy might win here
        for snake_id in list(spam_dict.keys()):
            gs.board.snake_dict[snake_id].delete_from_turn_prob(turn=turn, coord=coord)
            del spam_dict[snake_id]

    elif len(snake_lengths[longest_length]) == 1:
        # There is a longer snake. Delete shorter snakes
        for snake_id in list(spam_dict.keys()):
            snake = gs.board.snake_dict[snake_id]
            if snake.id == snake_lengths[longest_length][0].id:
                continue
            snake.delete_from_turn_prob(turn=turn, coord=coord)
            del spam_dict[snake.id]
    else:
        raise Exception(f"There isn't a longest snake?")

    return spam_dict


def resolve_collisions(gs: GameState, turn: int) -> None:
    combined_coord_prob_dict: dict[Coord, dict[str, Spam]] = {}

    # Since food restores the health this turn and causes the snake to grow the next turn,
    # I don't have to consider food on this level.
    for snake in gs.board.snake_dict.values():
        coord_prob_dict = get_coord_prob_dict(
            state_prob=100,
            body_coords=snake.body,
            health=snake.health,
            turn=turn,
            board_width=gs.board.width,
            board_height=gs.board.height,
        )
        snake.turn_prob[turn] = coord_prob_dict

        for coord, direction in coord_prob_dict.items():
            if combined_coord_prob_dict.get(coord) is None:
                combined_coord_prob_dict[coord] = {}
            combined_coord_prob_dict[coord][snake.id] = direction

    # Multiple snake bodies can't exist in the same square in the standard game mode
    # This condition reflects:
    # - A snake body and a potential snake move or
    # - Two potential snake moves
    for coord in combined_coord_prob_dict.keys():
        combined_coord_prob_dict[coord] = resolve_body_collisions(
            gs=gs, turn=turn, coord=coord, spam_dict=combined_coord_prob_dict[coord]
        )
    for coord in combined_coord_prob_dict.keys():
        combined_coord_prob_dict[coord] = resolve_head_collisions(
            gs=gs, turn=turn, coord=coord, spam_dict=combined_coord_prob_dict[coord]
        )
