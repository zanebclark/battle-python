from __future__ import annotations

from collections import defaultdict
from aws_lambda_powertools.utilities.parser import BaseModel
from aws_lambda_powertools import Logger


from pydantic import NonNegativeInt

from battle_python.SnakeState import SnakeState
from battle_python.api_types import Coord

logger = Logger()

DEATH = Coord(x=1000, y=1000)


class BoardState(BaseModel):
    turn: NonNegativeInt
    board_height: NonNegativeInt
    board_width: NonNegativeInt
    food_prob: dict[Coord, float]
    hazard_prob: dict[Coord, float]
    snake_states: list[SnakeState]
    hazard_damage_rate: int

    def get_legal_adjacent_coords(self, coord: Coord) -> list[Coord]:
        adj_coords = coord.get_adjacent()
        return [
            coord
            for coord in adj_coords
            if 0 <= coord.x <= self.board_width - 1
            and 0 <= coord.y <= self.board_height - 1
        ]

    def get_next_body(self, next_body: list[Coord]) -> list[Coord]:
        if next_body[0] in self.food_prob.keys():
            next_body.append(next_body[-1])
        return next_body

    def get_next_health(self, next_body: list[Coord], snake: SnakeState) -> int:
        next_health = snake.health - 1

        if next_body[0] in self.food_prob.keys():
            next_health = 100

        if next_body[0] in self.hazard_prob.keys():
            next_health -= self.hazard_damage_rate

        if next_health <= 0:
            return 0

        if next_health > 100:
            logger.warning(
                "Health is greater than 100. Not sure how that happened.",
                snake_id=snake.snake_id,
            )
            return 100

        return next_health

    def get_next_snake_state(
        self, snake: SnakeState, move: Coord, option_count: int
    ) -> SnakeState:
        next_state_prob = snake.state_prob / option_count
        next_body = self.get_next_body(next_body=[move, *snake.body[:-1]])
        next_health = self.get_next_health(next_body=next_body, snake=snake)
        next_death_prob = snake.death_prob
        if next_health == 0 or move is DEATH:
            next_death_prob = next_state_prob

        return snake.model_copy(
            update={
                "state_prob": next_state_prob,
                "death_prob": next_death_prob,
                "food_prob": next_death_prob,  # TODO: Fix this
                "murder_prob": next_death_prob,  # TODO: Fix this
                "health": next_health,
                "body": next_body,
                "head": next_body[0],
                "length": len(next_body),
                "prev_state": snake,
            },
            deep=True,
        )

    def get_next_snake_states(self) -> list[SnakeState]:
        next_states: list[SnakeState] = []

        snake_body_coords = [
            coord
            for snake in self.snake_states
            for coord in snake.body[:-1]
            if snake.state_prob == 1  # TODO: Make this configurable
        ]

        potential_snake_head_coords = [
            coord
            for snake in self.snake_states
            for coord in snake.head.get_adjacent()
            if not snake.is_self
            and snake.length >= snake.length
            and snake.state_prob >= float(1 / 3)  # TODO: Make this configurable
        ]

        for snake in self.snake_states:
            moves = self.get_legal_adjacent_coords(coord=snake.head)

            # Exclude body collisions and head collisions with larger snakes
            reasonable_moves = [
                move
                for move in moves
                if move not in snake_body_coords
                and move not in potential_snake_head_coords
            ]

            if len(reasonable_moves) == 0:
                reasonable_moves.append(DEATH)

            option_count = len(snake.reasonable_moves)

            for move in snake.reasonable_moves:
                next_states.append(
                    self.get_next_snake_state(
                        snake=snake,
                        move=move,
                        option_count=option_count,
                    )
                )

        return next_states

    def get_snake_heads_at_coord(self):
        snake_heads_at_coord: dict[Coord, list[SnakeState]] = defaultdict(list)
        for snake_state in self.snake_states:
            snake_heads_at_coord[snake_state.head].append(snake_state)
        return snake_heads_at_coord

    @staticmethod
    def resolve_head_collision(snake_heads_at_coord: list[SnakeState]):
        if len(snake_heads_at_coord) <= 1:
            return

        snake_heads_at_coord.sort(key=lambda snk: snk.length)
        longest_snake = snake_heads_at_coord[0]
        for other_snake in snake_heads_at_coord[1:]:
            if longest_snake.length == other_snake.length:
                longest_snake.death_prob += (
                    longest_snake.state_prob * other_snake.state_prob  # TODO: Suspect
                )
            else:
                longest_snake.murder_prob += (
                    longest_snake.state_prob * other_snake.state_prob  # TODO: Suspect
                )
            other_snake.death_prob += (
                longest_snake.state_prob * other_snake.state_prob  # TODO: Suspect
            )

    def resolve_food_probability(
        self,
        coord: Coord,
        snake_heads_at_coord: list[SnakeState],
    ):
        if coord in self.food_prob.keys():
            snake_heads_at_coord.sort(key=lambda snk: snk.length)
            longest_snake = snake_heads_at_coord[0]

            self.food_prob[coord] -= longest_snake.state_prob
            longest_snake.food_prob += self.food_prob[
                coord
            ]  # TODO: This isn't quite right

    def get_next_board(self) -> BoardState:
        next_board = BoardState(
            turn=self.turn + 1,
            board_width=self.board_width,
            board_height=self.board_height,
            food={**self.food_prob},
            hazards={
                **self.hazard_prob
            },  # TODO: Predict hazard zones: https://github.com/BattlesnakeOfficial/rules/blob/main/standard.go#L130
            snake_states=self.snake_states,
            hazard_damage_rate=self.hazard_damage_rate,
        )

        next_board.snake_states = next_board.get_next_snake_states()

        snake_heads_at_coord = next_board.get_snake_heads_at_coord()
        for coord, snake_heads_at_coord in snake_heads_at_coord.items():
            next_board.resolve_head_collision(snake_heads_at_coord=snake_heads_at_coord)
            next_board.resolve_food_probability(
                coord=coord, snake_heads_at_coord=snake_heads_at_coord
            )

        return next_board
