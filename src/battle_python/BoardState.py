from __future__ import annotations

from collections import defaultdict
from itertools import product
from typing import Literal

import numpy as np
import numpy.typing as npt
import numpy.ma as ma
from aws_lambda_powertools.utilities.parser import BaseModel
from aws_lambda_powertools import Logger

from pydantic import NonNegativeInt, Field, ConfigDict

from battle_python.SnakeState import SnakeState, Elimination
from battle_python.api_types import Coord, Game, SnakeDef
from battle_python.constants import (
    FOOD_WEIGHT,
    CENTER_CONTROL_WEIGHT,
    AREA_MULTIPLIER,
    DEATH_COORD,
    FOOD_SCORE,
    MURDER_SCORE,
    WIN_SCORE,
    DEATH_SCORE,
    UNEXPLORED_VALUE,
    BORDER_VALUE,
)
from battle_python.utils import get_aligned_masked_array

logger = Logger()


class BoardState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
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
    board_array: npt.NDArray[np.int_]
    food_array: npt.NDArray[np.int_]
    all_snake_bodies_array: npt.NDArray[np.int_]
    center_weight_array: npt.NDArray[np.int_]

    @staticmethod
    def get_board_array(board_width: int, board_height: int) -> npt.NDArray[np.int_]:
        # The first element is the # of rows (y-axis). The second element is the # of columns (x-axis)
        # Adding two supports padding the board with masked values. This supports calculations up to the
        # edge of the grid without altering the array size
        shape = (board_height + 2, board_width + 2)

        board_array = np.full(shape=shape, fill_value=BORDER_VALUE, dtype=np.int8)

        # Fill the actual board area with -1
        board_array[1:-1, 1:-1] = -1

        # print("board_array:")
        # print(get_aligned_masked_array(board_array))

        return board_array

    @staticmethod
    def get_food_array(
        board_array: npt.NDArray[np.int_], food_coords: tuple[Coord, ...]
    ) -> npt.NDArray[np.int_]:
        food_array = np.copy(board_array, subok=True)

        # Fill the actual board area with 1 to support element-wise multiplication
        food_array[1:-1, 1:-1] = 1

        rows, _ = food_array.shape
        food_array[
            [
                (rows - 2 - coord.y) for coord in food_coords
            ],  # Rows (y-axis) are the first element. Indexing is top to bottom
            [
                coord.x + 1 for coord in food_coords
            ],  # Rows (x-axis) are the second element. +1 for the pad
        ] = FOOD_WEIGHT

        # print("food_array:")
        # print(get_aligned_masked_array(food_array))

        return food_array

    @staticmethod
    def get_all_snake_bodies_array(
        board_array: npt.NDArray[np.int_], snakes: tuple[SnakeState, ...]
    ) -> npt.NDArray[np.int_]:
        all_snake_bodies_array = np.copy(board_array, subok=True)
        [
            np.putmask(
                all_snake_bodies_array,
                snake.body_array >= 0,
                snake.body_array,
            )
            for snake in snakes
            if snake.elimination is None
        ]

        # print("get_all_snake_bodies_array:")
        # print(get_aligned_masked_array(all_snake_bodies_array))

        return all_snake_bodies_array

    @staticmethod
    def get_center_weight_array(
        board_array: npt.NDArray[np.int_],
    ) -> npt.NDArray[np.int_]:
        center_weight = np.copy(board_array, subok=True)

        # Fill the actual board area with 1 to support element-wise multiplication
        center_weight[1:-1, 1:-1] = 1

        # Fill the center 3x3 with center control weight
        center_weight[5:-5, 5:-5] = CENTER_CONTROL_WEIGHT

        # print("center_weight:")
        # print(get_aligned_masked_array(center_weight))

        return center_weight

    @classmethod
    def factory(cls, **kwargs) -> BoardState:
        my_snake = kwargs["my_snake"]
        food_coords = kwargs["food_coords"]
        other_snakes = kwargs["other_snakes"]
        board_height = kwargs["board_height"]
        board_width = kwargs["board_width"]
        prev_state = kwargs.get("prev_state")
        snake_body_coords = [
            coord
            for snake in [my_snake, *other_snakes]
            for coord in snake.body[:-1]
            if snake.elimination is None
        ]

        if prev_state is None:
            board_array = cls.get_board_array(
                board_width=board_width, board_height=board_height
            )
            center_weight_array = cls.get_center_weight_array(board_array=board_array)
        else:
            board_array = prev_state.board_array
            center_weight_array = prev_state.center_weight_array

        food_array = cls.get_food_array(
            board_array=board_array, food_coords=food_coords
        )

        all_snake_bodies_array = cls.get_all_snake_bodies_array(
            board_array=board_array, snakes=(my_snake, *other_snakes)
        )

        [
            snake.set_moves_array(all_snake_bodies_array)
            for snake in [my_snake, *other_snakes]
        ]

        return cls(
            snake_body_coords=snake_body_coords,
            board_array=board_array,
            food_array=food_array,
            all_snake_bodies_array=all_snake_bodies_array,
            center_weight_array=center_weight_array,
            **kwargs,
        )

    def get_my_snake_area_of_control(self) -> npt.NDArray[np.int_]:
        """
        Returns a 2D array that represents my snake's "area of control".
        Coordinates with a value of 0 are reachable by least one enemy snake before me.

        For example:
        Another snake can get to a coordinate at move 4
        I can get to the same coordinate at move 14,
        The element-wise subtraction will produce -10.
        The value will be set to 0 at this coordinate to reflect that I can't reach it before my opponent

        Another example:
        Another snake can get to a coordinate at move 10
        I can get to the same coordinate at move 3,
        The element-wise subtraction will produce 7.
        The value at this coordinate will be 7
        """
        move = 0
        continue_iterating = True
        while continue_iterating:
            for snake in [self.my_snake, *self.other_snakes]:
                if snake.moves_exhausted:
                    if snake.is_self:
                        continue_iterating = False
                        break
                    continue
                snake.iterate_moves_array(move=move)
                # print(f"snake {snake.id}")
                # print(get_aligned_masked_array(snake.moves_array))

            if np.all(
                np.logical_or.reduce(
                    [
                        (snake.moves_array != UNEXPLORED_VALUE)
                        for snake in [self.my_snake, *self.other_snakes]
                    ]
                )
            ):
                continue_iterating = False

            move += 1

        for snake in [self.my_snake, *self.other_snakes]:
            snake.moves_array.soften_mask()
            snake.moves_array.mask = False

        my_snake_voronoi = np.copy(self.my_snake.moves_array, subok=True)
        [
            np.putmask(
                my_snake_voronoi,
                (snake.moves_array - self.my_snake.moves_array) <= 0,
                0,
            )
            for snake in self.other_snakes
            if snake.elimination is None
        ]
        # print("my_snake_voronoi")
        # print(get_aligned_masked_array(my_snake_voronoi))
        return my_snake_voronoi

    def spam(self):
        area_of_control = self.get_my_snake_area_of_control()
        my_snake_score = np.copy(area_of_control, subok=True)

        # Replace non-zero values with an area multiplier
        np.putmask(
            my_snake_score,
            my_snake_score > 0,
            AREA_MULTIPLIER,
        )

        score = np.multiply(my_snake_score, self.food_array)

        score = np.multiply(score, self.center_weight_array)

        # print("score")
        # print(get_aligned_masked_array(score))

        return score.sum()

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

        return SnakeState.factory(
            board_array=self.board_array,
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
