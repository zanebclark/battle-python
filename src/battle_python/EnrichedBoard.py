from __future__ import annotations

from collections import defaultdict


from pydantic import NonNegativeInt

from battle_python.SnakeState import SnakeState
from battle_python.api_types import FrozenBaseModel, Coord


class EnrichedBoard(FrozenBaseModel):
    turn: NonNegativeInt
    board_height: NonNegativeInt
    board_width: NonNegativeInt
    food_prob: dict[Coord, float]
    hazard_prob: dict[Coord, float]
    snake_states: list[SnakeState]

    def get_legal_adjacent_coords(self, coord: Coord) -> list[Coord]:
        adj_coords = coord.get_adjacent()
        return [
            coord
            for coord in adj_coords
            if 0 <= coord.x <= self.board_width - 1
            and 0 <= coord.y <= self.board_height - 1
        ]

    def get_next_board(self) -> EnrichedBoard:
        next_food_prob: dict[Coord, float] = {**self.food_prob}
        next_snake_states = [
            state
            for next_states in self.snake_states
            for state in next_states.get_next_states(board=self)
        ]

        heads_at_coord: dict[Coord, list[SnakeState]] = defaultdict(list)
        for next_snake_state in next_snake_states:
            heads_at_coord[next_snake_state.head].append(next_snake_state)

        # Resolve head collisions and food_prob consumption
        for coord, snake_states in heads_at_coord.items():
            # Resolve head collisions
            if len(snake_states) > 1:
                snake_states.sort(key=lambda snk: snk.length)
                longest_snake = snake_states[0]
                for other_snake in snake_states[1:]:
                    if longest_snake.length == other_snake.length:
                        longest_snake.death_prob += (
                            longest_snake.state_prob * other_snake.state_prob
                        )
                    else:
                        longest_snake.murder_prob += (
                            longest_snake.state_prob * other_snake.state_prob
                        )
                    other_snake.death_prob += (
                        longest_snake.state_prob * other_snake.state_prob
                    )

            if coord in next_food_prob.keys():
                for snake in snake_states:
                    next_food_prob[coord] -= snake.state_prob
                    snake.food_prob += next_food_prob[
                        coord
                    ]  # TODO: This isn't quite right
                    snake.health = 100
                    snake.body.append(snake.body[-1])
                    snake.length += 1

        return EnrichedBoard(
            turn=self.turn + 1,
            board_width=self.board_width,
            board_height=self.board_height,
            food=next_food_prob,
            hazards=self.hazard_prob,  # TODO: Predict hazard zones
            snake_states=next_snake_states,
        )
