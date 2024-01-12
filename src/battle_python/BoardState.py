from __future__ import annotations

from collections import defaultdict
from itertools import product

from aws_lambda_powertools.utilities.parser import BaseModel
from aws_lambda_powertools import Logger


from pydantic import NonNegativeInt

from battle_python.SnakeState import SnakeState
from battle_python.api_types import Coord

logger = Logger()

DEATH = Coord(x=1000, y=1000)


class BoardState(BaseModel):
    turn: NonNegativeInt
    board_width: NonNegativeInt
    board_height: NonNegativeInt
    food_coords: list[Coord]
    hazard_coords: list[Coord]
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

    def get_next_body(self, current_body: list[Coord]) -> list[Coord]:
        if current_body[0] in self.food_coords:
            current_body.append(current_body[-1])
        return current_body

    def is_food_consumed(self, next_body: list[Coord]) -> bool:
        if next_body[0] in self.food_coords:
            return True
        return False

    def get_next_health(
        self,
        next_body: list[Coord],
        food_consumed: bool,
        snake: SnakeState,
    ) -> int:
        next_health = snake.health - 1

        if food_consumed:
            next_health = 100
        elif next_body[0] in self.hazard_coords:
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

    def get_next_snake_state(self, snake: SnakeState, move: Coord) -> SnakeState:
        next_body = self.get_next_body(current_body=[move, *snake.body[:-1]])
        food_consumed = self.is_food_consumed(next_body=next_body)
        next_health = self.get_next_health(
            next_body=next_body, food_consumed=food_consumed, snake=snake
        )

        return snake.model_copy(
            update={
                "health": next_health,
                "body": next_body,
                "head": next_body[0],
                "length": len(next_body),
                "food_consumed": [next_body[0], *snake.food_consumed]
                if food_consumed
                else snake.food_consumed,
                "is_eliminated": next_health == 0 or move is DEATH,
                "prev_state": snake,
            },
            deep=True,
        )

    def get_next_snake_states_per_snake(self) -> dict[str, list[SnakeState]]:
        next_states: dict[str, list[SnakeState]] = defaultdict(list)

        snake_body_coords = [
            coord
            for snake in self.snake_states
            for coord in snake.body[:-1]
            if not snake.is_eliminated
        ]

        for snake in self.snake_states:
            if snake.is_eliminated:
                continue

            moves = self.get_legal_adjacent_coords(coord=snake.head)

            # Exclude body collisions
            reasonable_moves = [move for move in moves if move not in snake_body_coords]

            if len(reasonable_moves) == 0:
                reasonable_moves.append(DEATH)

            for move in reasonable_moves:
                next_states[snake.snake_id].append(
                    self.get_next_snake_state(snake=snake, move=move)
                )

        return next_states

    def get_snake_heads_at_coord(self):
        snake_heads_at_coord: dict[Coord, list[SnakeState]] = defaultdict(list)
        for snake_state in self.snake_states:
            if snake_state.is_eliminated:
                continue
            snake_heads_at_coord[snake_state.head].append(snake_state)
        return snake_heads_at_coord

    @staticmethod
    def resolve_head_collision(snake_heads_at_coord: list[SnakeState]) -> None:
        if len(snake_heads_at_coord) <= 1:
            return

        snake_heads_at_coord.sort(key=lambda snk: snk.length, reverse=True)
        longest_snake = snake_heads_at_coord[0]
        for other_snake in snake_heads_at_coord[1:]:
            if longest_snake.length == other_snake.length:
                longest_snake.is_eliminated = True
            else:
                longest_snake.murder_count += 1
            other_snake.is_eliminated = True

    def resolve_food_consumption(
        self,
        coord: Coord,
        snake_heads_at_coord: list[SnakeState],
    ):
        if coord not in self.food_coords:
            # Not a food coord
            return
        survivors = [snake for snake in snake_heads_at_coord if not snake.is_eliminated]
        if len(survivors) == 0:
            # Collision killed all of the snakes
            return
        if len(survivors) > 1:
            logger.warning(
                f"More than one snake at a food coord", {"survivors": survivors}
            )
        survivor = survivors[0]
        self.food_coords.remove(coord)
        survivor.food_consumed.append(coord)

    def get_next_boards(self) -> list[BoardState]:
        next_boards: list[BoardState] = []
        next_snake_states_per_snake = self.get_next_snake_states_per_snake()
        all_potential_snake_states = product(*next_snake_states_per_snake.values())

        for potential_snake_states in all_potential_snake_states:
            # TODO: Predict hazard zones: https://github.com/BattlesnakeOfficial/rules/blob/main/standard.go#L130
            potential_board = BoardState(
                turn=self.turn + 1,
                board_width=self.board_width,
                board_height=self.board_height,
                food_coords=self.food_coords,
                hazard_coords=self.hazard_coords,
                snake_states=[state.model_copy() for state in potential_snake_states],
                hazard_damage_rate=self.hazard_damage_rate,
            )

            snake_heads_at_coord = potential_board.get_snake_heads_at_coord()
            for coord, snake_heads_at_coord in snake_heads_at_coord.items():
                potential_board.resolve_head_collision(
                    snake_heads_at_coord=snake_heads_at_coord
                )
                potential_board.resolve_food_consumption(
                    coord=coord, snake_heads_at_coord=snake_heads_at_coord
                )

            next_boards.append(potential_board)
        return next_boards
