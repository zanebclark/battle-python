from __future__ import annotations

from collections import defaultdict
from itertools import product
from typing import Literal

from aws_lambda_powertools.utilities.parser import BaseModel
from aws_lambda_powertools import Logger


from pydantic import NonNegativeInt, Field

from battle_python.SnakeState import SnakeState, Elimination
from battle_python.api_types import Coord, Game, SnakeDef

logger = Logger()


DEATH_SCORE = -1000
WIN_SCORE = abs(DEATH_SCORE)
FOOD_SCORE = 100
MURDER_SCORE = 100
DEATH_COORD = Coord(x=1000, y=1000)


class BoardState(BaseModel):
    turn: NonNegativeInt
    board_width: NonNegativeInt
    board_height: NonNegativeInt
    food_coords: tuple[Coord, ...]
    hazard_coords: tuple[Coord, ...]
    other_snakes: tuple[SnakeState, ...]
    my_snake: SnakeState
    snake_body_coords: tuple[Coord, ...]
    hazard_damage_rate: int
    prev_state: BoardState | None = None
    next_boards: list[BoardState] = Field(default_factory=list)
    is_terminal: bool = False
    terminal_reason: Literal["duplicate", "self_eliminated", "victory"] | None = None
    score: float = 0

    def get_flood_fill_coords(
        self, coord: Coord, max_depth: int, depth: int = 0
    ) -> set[Coord]:
        if depth >= max_depth:
            return {coord}
        moves = self.get_legal_adjacent_coords(coord=coord)
        return {
            coord
            for move in moves
            for coord in self.get_flood_fill_coords(
                coord=move, depth=depth + 1, max_depth=max_depth
            )
            if move not in self.snake_body_coords
            and move not in {snake.head for snake in self.other_snakes}
        }

    @classmethod
    def factory(cls, **kwargs) -> BoardState:
        my_snake = kwargs["my_snake"]
        other_snakes = kwargs["other_snakes"]
        snake_body_coords = [
            coord
            for snake in [my_snake, *other_snakes]
            for coord in snake.body[:-1]
            if snake.elimination is None
        ]
        return cls(snake_body_coords=snake_body_coords, **kwargs)

    def get_my_key(self) -> tuple[int, tuple[Coord]]:
        return self.turn, self.my_snake.body[0]

    def get_other_key(self) -> tuple:
        snake_states = tuple(
            (
                snake.id,
                snake.health,
                snake.body,
            )
            for snake in sorted(self.other_snakes, key=lambda snake: snake.id)
        )

        return (
            self.food_coords,
            (
                self.my_snake.id,
                self.my_snake.health,
                self.my_snake.body,
            ),
            snake_states,
        )

    def get_legal_adjacent_coords(self, coord: Coord) -> set[Coord]:
        adj_coords = coord.get_adjacent()
        return {
            coord
            for coord in adj_coords
            if 0 <= coord.x <= self.board_width - 1
            and 0 <= coord.y <= self.board_height - 1
        }

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
                snake_id=snake.id,
            )
            return 100

        return next_health

    def get_next_snake_state_for_snake_move(
        self, snake: SnakeState, move: Coord
    ) -> SnakeState:
        # TODO: Add an eliminated by object. Mirror what they're doing with board and rules
        next_body = self.get_next_body(current_body=[move, *snake.body[:-1]])
        food_consumed = self.is_food_consumed(next_body=next_body)
        next_health = self.get_next_health(
            next_body=next_body, food_consumed=food_consumed, snake=snake
        )
        food_consumed_coords = [*snake.food_consumed]
        if food_consumed:
            food_consumed_coords.append(next_body[0])

        elimination = None
        if next_health == 0:
            elimination = Elimination(cause="out-of-health")

        if move is DEATH_COORD:
            elimination = Elimination(cause="wall-collision")

        return SnakeState(
            id=snake.id,
            health=next_health,
            body=next_body,
            head=next_body[0],
            length=len(next_body),
            latency=snake.latency,
            shout=snake.shout,
            is_self=snake.is_self,
            murder_count=snake.murder_count,
            food_consumed=food_consumed_coords,
            elimination=elimination,
            prev_state=snake,
        )

    def get_next_snake_states_for_snake(self, snake: SnakeState) -> list[SnakeState]:
        if snake.elimination is not None:
            return []

        moves = self.get_legal_adjacent_coords(coord=snake.head)

        # Exclude body collisions
        reasonable_moves = [
            move for move in moves if move not in self.snake_body_coords
        ]

        if len(reasonable_moves) == 0:
            reasonable_moves.append(DEATH_COORD)

        if (
            len(reasonable_moves) > 1
            and not snake.is_self
            and self.my_snake.head.get_manhattan_distance(snake.head) > 4
        ):
            if (
                self.turn % 2 == 1
                and snake.body[0] + snake.last_move in reasonable_moves
            ):
                reasonable_moves = [snake.body[0] + snake.last_move]
            else:
                reasonable_moves = [
                    move
                    for move in reasonable_moves
                    if self.my_snake.head.get_manhattan_distance(move)
                    < self.my_snake.head.get_manhattan_distance(snake.head)
                ]

        return [
            self.get_next_snake_state_for_snake_move(snake=snake, move=move)
            for move in reasonable_moves
        ]

    def get_snake_heads_at_coord(self) -> dict[Coord, list[SnakeState]]:
        snake_heads_at_coord: dict[Coord, list[SnakeState]] = defaultdict(list)
        for snake_state in self.other_snakes:
            if snake_state.elimination is not None:
                continue
            snake_heads_at_coord[snake_state.head].append(snake_state)

        snake_heads_at_coord[self.my_snake.head].append(self.my_snake)

        return snake_heads_at_coord

    def resolve_head_collision(self, snake_heads_at_coord: list[SnakeState]) -> None:
        if len(snake_heads_at_coord) <= 1:
            return

        snake_heads_at_coord.sort(key=lambda snk: snk.length, reverse=True)
        longest_snake = snake_heads_at_coord[0]
        for other_snake in snake_heads_at_coord[1:]:
            if longest_snake.length == other_snake.length:
                longest_snake.elimination = Elimination(
                    cause="head-collision", by=other_snake.id
                )
            else:
                longest_snake.murder_count += 1
                if longest_snake.id == self.my_snake.id:
                    self.score += MURDER_SCORE
            other_snake.elimination = Elimination(
                cause="head-collision", by=longest_snake.id
            )

    def resolve_food_consumption(
        self,
        coord: Coord,
        snake_heads_at_coord: list[SnakeState],
    ):
        if coord not in self.food_coords:
            # Not a food coordinate
            return
        survivors = [
            snake for snake in snake_heads_at_coord if snake.elimination is None
        ]
        if len(survivors) == 0:
            # Collision killed all the snakes
            return
        if len(survivors) > 1:
            logger.warning(
                f"More than one snake at a food coord", {"survivors": survivors}
            )
        survivor = survivors[0]
        self.food_coords = tuple(
            (f_coord for f_coord in self.food_coords if f_coord != coord)
        )
        survivor.food_consumed = (*survivor.food_consumed, coord)

        if survivor.id == self.my_snake.id:
            self.score += FOOD_SCORE

    def model_post_init(self, __context) -> None:
        snake_heads_at_coord = self.get_snake_heads_at_coord()
        for coord, snake_heads_at_coord in snake_heads_at_coord.items():
            self.resolve_head_collision(snake_heads_at_coord=snake_heads_at_coord)
            self.resolve_food_consumption(
                coord=coord, snake_heads_at_coord=snake_heads_at_coord
            )

        if self.my_snake.elimination is not None:
            self.score = DEATH_SCORE
            self.is_terminal = True
            self.terminal_reason = "self_eliminated"
            return

        if len(self.other_snakes) == 0:
            self.is_terminal = True
            self.terminal_reason = "victory"
            self.score = WIN_SCORE
            return

    def populate_next_boards(self) -> None:
        if self.is_terminal:
            return

        my_snake_next_states = self.get_next_snake_states_for_snake(snake=self.my_snake)
        other_snakes_next_states = [
            other_snake_next_state
            for other_snake_next_state in [
                self.get_next_snake_states_for_snake(snake=snake)
                for snake in self.other_snakes
            ]
            if len(other_snake_next_state) > 0
        ]
        all_potential_snake_states: tuple[list[SnakeState]] = product(
            my_snake_next_states, *other_snakes_next_states
        )

        for potential_snake_states in all_potential_snake_states:
            # TODO: Predict hazard zones: https://github.com/BattlesnakeOfficial/rules/blob/main/standard.go#L130
            potential_board = BoardState.factory(
                turn=self.turn + 1,
                board_width=self.board_width,
                board_height=self.board_height,
                food_coords=self.food_coords,
                hazard_coords=self.hazard_coords,
                my_snake=potential_snake_states[0].model_copy(),
                other_snakes=[
                    snake.model_copy() for snake in potential_snake_states[1:]
                ],
                hazard_damage_rate=self.hazard_damage_rate,
                prev_state=self,
            )
            self.next_boards.append(potential_board)

    def get_snake_payload(
        self,
        snake_defs: dict[str, SnakeDef],
        snake_id: str | None = None,
        me: bool = False,
    ) -> dict:
        if snake_id:
            snake = [
                snake
                for snake in [self.my_snake, *self.other_snakes]
                if snake.id == snake_id
            ]
            if len(snake) == 0:
                return {
                    "id": snake_id,
                    "name": snake_defs[snake_id].name,
                    "health": 0,
                    "body": [],
                    "latency": 0,
                    "length": 0,
                    "customizations": snake_defs[snake_id].customizations.model_dump(),
                    "elimination": Elimination(cause="unknown", by="unknown"),
                }
            snake = snake[0]
        elif me:
            snake = self.my_snake
        else:
            raise Exception("either the id or me must be supplied")

        return {
            "id": snake.id,
            "name": snake_defs[snake.id].name,
            "health": snake.health,
            "body": [{"x": coord.x, "y": coord.y} for coord in snake.body],
            "latency": str(snake.latency),
            "length": snake.length,
            "customizations": snake_defs[snake.id].customizations.model_dump(),
            "elimination": snake.elimination.model_dump()
            if snake.elimination is not None
            else None,
        }

    def get_board_payload(self, snake_defs: dict[str, SnakeDef], game: Game) -> dict:
        return {
            "game": game.model_dump(),
            "turn": self.turn,
            "board": {
                "height": self.board_height,
                "width": self.board_width,
                "food": [{"x": coord.x, "y": coord.y} for coord in self.food_coords],
                "hazards": [
                    {"x": coord.x, "y": coord.y} for coord in self.hazard_coords
                ],
                "snakes": [
                    self.get_snake_payload(snake_id=snake.id, snake_defs=snake_defs)
                    for snake in [self.my_snake, *self.other_snakes]
                ],
            },
            "you": self.get_snake_payload(me=True, snake_defs=snake_defs),
            "terminalReason": self.terminal_reason,
            "descendents": [
                next_board.get_board_payload(snake_defs=snake_defs, game=game)
                for next_board in self.next_boards
            ],
        }
