from __future__ import annotations

from collections import defaultdict
from itertools import product
from typing import ClassVar

from aws_lambda_powertools.utilities.parser import BaseModel
from aws_lambda_powertools import Logger


from pydantic import NonNegativeInt, Field, model_validator

from battle_python.SnakeState import SnakeState
from battle_python.api_types import Coord, Game, SnakeDef

logger = Logger()

DEATH_SCORE = float("inf")
FOOD_SCORE = 100
MURDER_SCORE = 100
DEATH_COORD = Coord(x=1000, y=1000)
explored_states_count = 0


def print_explored_states_count():
    print(f"explored_states_count: {explored_states_count}")


class BoardState(BaseModel):
    explored_states: ClassVar[set[tuple]] = set()

    turn: NonNegativeInt
    board_width: NonNegativeInt
    board_height: NonNegativeInt
    food_coords: list[Coord]
    hazard_coords: list[Coord]
    snake_states: list[SnakeState]
    my_snake_state: SnakeState | None = None
    hazard_damage_rate: int
    prev_state: BoardState | None = None
    next_boards: list[BoardState] = Field(default_factory=list)
    is_terminal: bool = False
    score: float = 0

    def get_dict_key(self) -> tuple:
        food_coords = tuple((coord.x, coord.y) for coord in sorted(self.food_coords))
        snake_states = tuple(
            (
                snake.snake_id,
                snake.health,
                tuple((coord.x, coord.y) for coord in snake.body),
            )
            for snake in sorted(self.snake_states, key=lambda snake: snake.snake_id)
        )

        return self.turn, food_coords, snake_states

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
        # TODO: Add an eliminated by object. Mirror what they're doing with board and rules
        next_body = self.get_next_body(current_body=[move, *snake.body[:-1]])
        food_consumed = self.is_food_consumed(next_body=next_body)
        next_health = self.get_next_health(
            next_body=next_body, food_consumed=food_consumed, snake=snake
        )
        food_consumed_coords = [*snake.food_consumed]
        if food_consumed:
            food_consumed_coords.append(next_body[0])

        return snake.model_copy(
            update={
                "health": next_health,
                "body": next_body,
                "head": next_body[0],
                "length": len(next_body),
                "food_consumed": food_consumed_coords,
                "is_eliminated": next_health == 0 or move is DEATH_COORD,
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
                reasonable_moves.append(DEATH_COORD)
            if len(reasonable_moves) > 1 and not snake.is_self:
                reasonable_moves = [
                    move
                    for move in reasonable_moves
                    if self.my_snake_state.head.get_manhattan_distance(move)
                    < self.my_snake_state.head.get_manhattan_distance(snake.head)
                ]

            [
                next_states[snake.snake_id].append(
                    self.get_next_snake_state(snake=snake, move=move)
                )
                for move in reasonable_moves
            ]

        return next_states

    def get_snake_heads_at_coord(self) -> dict[Coord, list[SnakeState]]:
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

    @model_validator(mode="after")
    def post_init(self):
        snake_heads_at_coord = self.get_snake_heads_at_coord()
        for coord, snake_heads_at_coord in snake_heads_at_coord.items():
            self.resolve_head_collision(snake_heads_at_coord=snake_heads_at_coord)
            self.resolve_food_consumption(
                coord=coord, snake_heads_at_coord=snake_heads_at_coord
            )

        dict_key = self.get_dict_key()
        if (
            self.turn != 0
        ):  # TODO: I'm not sure why this is being visited twice on the first turn
            if dict_key in self.explored_states:
                self.is_terminal = True
            else:
                self.explored_states.add(dict_key)

        for snake in self.snake_states:
            if snake.is_self:
                self.my_snake_state = snake
                break

        if self.my_snake_state is None or self.my_snake_state.is_eliminated:
            self.is_terminal = True

        if len(self.snake_states) == 1:
            self.is_terminal = True

        self.score = self.score_state()

        return self

    def populate_next_boards(self, max_turn: int) -> None:
        if self.turn >= max_turn or self.is_terminal:
            return None

        next_snake_states_per_snake = self.get_next_snake_states_per_snake()
        all_potential_snake_states: tuple[list[SnakeState]] = product(
            *next_snake_states_per_snake.values()
        )

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
                prev_state=self,
            )

            self.next_boards.append(potential_board)
            potential_board.populate_next_boards(max_turn=max_turn)

        self.score = sum([board.score for board in self.next_boards]) / len(
            self.next_boards
        )
        return None

    def score_state(self) -> float:
        if self.my_snake_state is None or self.my_snake_state.is_eliminated:
            return 0
        if len(self.snake_states) == 1:
            return 100000  # You've won!
        return 1

    def get_snake_payload(
        self,
        snake_defs: dict[str, SnakeDef],
        snake_id: str | None = None,
        me: bool = False,
    ) -> dict:
        if snake_id:
            snake = [snake for snake in self.snake_states if snake.snake_id == snake_id]
        elif me:
            snake = [snake for snake in self.snake_states if snake.is_self]
        else:
            raise Exception("either the snake_id or me must be supplied")
        if len(snake) == 0:
            return {
                "id": snake_id,
                "name": snake_defs[snake_id].name,
                "health": 0,
                "body": [],
                "latency": 0,
                "length": 0,
                "customizations": snake_defs[snake_id].customizations.model_dump(),
            }
        snake = snake[0]
        snake_id = snake.snake_id
        return {
            "id": snake.snake_id,
            "name": snake_defs[snake_id].name,
            "health": snake.health,
            "body": [coord.model_dump() for coord in snake.body],
            "latency": str(snake.latency),
            "length": snake.length,
            "customizations": snake_defs[snake_id].customizations.model_dump(),
        }

    def get_board_payload(self, snake_defs: dict[str, SnakeDef], game: Game) -> dict:
        global explored_states_count
        explored_states_count += 1
        return {
            "game": game.model_dump(),
            "turn": self.turn,
            "board": {
                "height": self.board_height,
                "width": self.board_width,
                "food": [coord.model_dump() for coord in self.food_coords],
                "hazards": [coord.model_dump() for coord in self.hazard_coords],
                "snakes": [
                    self.get_snake_payload(
                        snake_id=snake.snake_id, snake_defs=snake_defs
                    )
                    for snake in self.snake_states
                ],
            },
            "you": self.get_snake_payload(me=True, snake_defs=snake_defs),
            "descendents": [
                next_board.get_board_payload(snake_defs=snake_defs, game=game)
                for next_board in self.next_boards
            ],
        }
