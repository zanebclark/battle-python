from __future__ import annotations

from collections import defaultdict
from itertools import product
from typing import Literal, Any, Generator
import structlog
import numpy as np
from numpy._typing import _8Bit
from numpy.ma import masked_where

from pydantic import NonNegativeInt, Field, ConfigDict, BaseModel

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
    UNEXPLORED_VALUE,
    BORDER_VALUE,
    SNAKE_BODY_VALUE,
)

log = structlog.get_logger()


def get_board_array(
    board_width: int, board_height: int
) -> np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]]:
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


def get_center_weight_array(
    board_array: np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]],
) -> np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]]:
    center_weight = np.copy(board_array, subok=True)

    # Fill the actual board area with 1 to support element-wise multiplication
    center_weight[1:-1, 1:-1] = 1

    # Fill the center 3x3 with center control weight
    center_weight[5:-5, 5:-5] = CENTER_CONTROL_WEIGHT

    # print("center_weight:")
    # print(get_aligned_masked_array(center_weight))

    return center_weight


def get_food_array(
    board_array: np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]],
    food_coords: tuple[Coord, ...],
) -> np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]]:
    food_array = np.copy(board_array, subok=True)

    # Fill the actual board area with 1 to support element-wise multiplication
    food_array[1:-1, 1:-1] = 1
    if len(food_coords) == 0:
        return food_array

    row_count, _ = food_array.shape

    # Rows (y-axis) are the first element. Indexing is top to bottom
    rows = [(row_count - 2 - coord.y) for coord in food_coords]
    # Rows (x-axis) are the second element. +1 for the pad
    columns = [coord.x + 1 for coord in food_coords]

    if any([ind < 0 for ind in [*rows, *columns]]):
        raise Exception(f"food coordinate outside of board: {food_coords}")

    food_array[rows, columns] = FOOD_WEIGHT

    # print("food_array:")
    # print(get_aligned_masked_array(food_array))

    return food_array


def get_snake_heads_at_coord(
    snakes: tuple[SnakeState, ...]
) -> dict[Coord, list[SnakeState]]:
    snake_heads_at_coord: dict[Coord, list[SnakeState]] = defaultdict(list)
    for snake_state in snakes:
        if snake_state.elimination is not None:
            continue
        snake_heads_at_coord[snake_state.head].append(snake_state)

    return snake_heads_at_coord


def resolve_head_collision(snake_heads_at_coord: list[SnakeState]) -> None:
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
        other_snake.elimination = Elimination(
            cause="head-collision", by=longest_snake.id
        )


def resolve_food_consumption(
    coord: Coord, snake_heads_at_coord: list[SnakeState], food_coords: tuple[Coord, ...]
) -> tuple[Coord, ...]:
    if coord not in food_coords:
        # Not a food coordinate
        return food_coords
    survivors = [snake for snake in snake_heads_at_coord if snake.elimination is None]
    if len(survivors) == 0:
        # Collision killed all the snakes
        return food_coords
    if len(survivors) > 1:
        log.warning(f"More than one snake at a food coord", {"survivors": survivors})
    survivor = survivors[0]
    survivor.food_consumed = (*survivor.food_consumed, coord)
    return tuple((f_coord for f_coord in food_coords if f_coord != coord))


def get_all_snake_bodies_array(
    board_array: np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]],
    snakes: tuple[SnakeState, ...],
) -> np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]]:
    row_count, _ = board_array.shape
    snake_body_array = np.array(board_array, copy=True)
    snake_body_array[1:-1, 1:-1] = UNEXPLORED_VALUE

    all_snake_bodies_array = np.array(
        [
            np.copy(snake_body_array, subok=True)
            for snake in snakes
            if snake.elimination is None
        ]
    )

    # Set snake bodies as SNAKE_BODY_VALUE on every slice
    for i, snake in enumerate(snakes):
        if snake.elimination is not None:
            continue

        # Rows (y-axis) are the first element. Indexing is top to bottom
        rows = [(row_count - 2 - coord.y) for coord in snake.body[:-1]]

        # Rows (x-axis) are the second element. +1 for the pad
        columns = [coord.x + 1 for coord in snake.body[:-1]]

        if any([ind < 0 for ind in [*rows, *columns]]):
            raise Exception(
                f"Snake {snake.id} body coordinates outside of board: {snake.body}"
            )

        all_snake_bodies_array[:, rows, columns] = SNAKE_BODY_VALUE

    # Set the snake's head as 0 on its slice
    # The first element references rows (y-axis). The second argument references columns (x-axis)
    # Rows are indexed from top to bottom. Subtract y coord from rows to account for this
    # Subtract 2 to account for board buffer rows on top and bottom
    # Add 1 to x to account for left-most board buffer
    for i, snake in enumerate([snake for snake in snakes if snake.elimination is None]):
        all_snake_bodies_array[
            i,
            # Rows (y-axis) are the first element. Indexing is top to bottom
            row_count - 2 - snake.head.y,
            # Rows (x-axis) are the second element. +1 for the pad
            snake.head.x + 1,
        ] = 0

    return all_snake_bodies_array


def get_all_snake_moves_array(
    all_snake_bodies_array: np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]],
) -> np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]]:
    all_snake_moves_array = np.copy(all_snake_bodies_array, subok=True)
    move = 0
    while True:
        masked_all_snakes = masked_where(  # type: ignore
            np.logical_and(
                all_snake_moves_array != UNEXPLORED_VALUE,
                all_snake_moves_array != move,
            ),
            all_snake_moves_array,
            copy=False,
        )
        masked_all_snakes.harden_mask()

        # Get indices of all Von Neumann Neighbors of elements where element == current move
        neighbors = [
            ind + shift
            for shift in [(0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
            for ind in np.argwhere(masked_all_snakes == move)
        ]

        if len(neighbors) == 0:
            break

        masked_all_snakes[
            [ind[0] for ind in neighbors],
            [ind[1] for ind in neighbors],
            [ind[2] for ind in neighbors],
        ] = (
            move + 1
        )

        move += 1

        # for i, snake in enumerate(masked_all_snakes):
        #     print(f"snake {i}")
        #     print(get_aligned_masked_array(snake))

    # Address inaccessible areas
    np.putmask(
        all_snake_moves_array,
        all_snake_moves_array == UNEXPLORED_VALUE,
        0,
    )

    # print("all_snake_moves_array:")
    # print(get_aligned_masked_array(all_snake_moves_array))

    return all_snake_moves_array


def get_my_snake_area_of_control(
    all_snake_moves_array: np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]],
) -> np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]]:
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
    if all_snake_moves_array.size == 0:
        return all_snake_moves_array

    my_snake_area_of_control = np.copy(all_snake_moves_array[0], subok=True)

    snakes, _, _ = all_snake_moves_array.shape

    if snakes == 1:
        np.putmask(
            my_snake_area_of_control,
            np.logical_or(
                my_snake_area_of_control == BORDER_VALUE,
                my_snake_area_of_control == SNAKE_BODY_VALUE,
            ),
            0,
        )
        return my_snake_area_of_control

    [
        np.putmask(  # type: ignore
            my_snake_area_of_control,
            (snake_moves - all_snake_moves_array[0]) <= 0,
            0,
        )
        for snake_moves in all_snake_moves_array[1:]
    ]

    # print("my_snake_area_of_control")
    # print(get_aligned_masked_array(my_snake_area_of_control))

    return my_snake_area_of_control


def get_score(
    my_snake: SnakeState,
    food_array: np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]],
    center_weight_array: np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]],
    all_snake_moves_array: np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]],
) -> int:
    if all_snake_moves_array.size == 0:
        return 0

    area_of_control = get_my_snake_area_of_control(
        all_snake_moves_array=all_snake_moves_array
    )
    my_snake_score = np.copy(area_of_control, subok=True)

    # Replace non-zero values with an area multiplier
    np.putmask(
        my_snake_score,
        my_snake_score > 0,
        AREA_MULTIPLIER,
    )

    score_board = np.multiply(my_snake_score, food_array)

    score_board = np.multiply(score_board, center_weight_array)

    # print("score_board")
    # print(get_aligned_masked_array(score_board))
    score = score_board.sum()

    score += MURDER_SCORE * my_snake.murder_count

    score += FOOD_SCORE * len(my_snake.food_consumed)

    return score


class BoardState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    turn: NonNegativeInt
    board_width: NonNegativeInt
    board_height: NonNegativeInt
    food_coords: tuple[Coord, ...]
    hazard_coords: tuple[Coord, ...]
    other_snakes: tuple[SnakeState, ...]
    my_snake: SnakeState
    hazard_damage_rate: int
    prev_state: BoardState | None = Field(default=None, exclude=True)
    next_boards: list[BoardState] = Field(default_factory=list, exclude=True)
    is_terminal: bool = False
    terminal_reason: Literal[
        "duplicate", "self_eliminated", "victory", "better-snake-state-available"
    ] | None = None
    board_array: np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]] = Field(
        exclude=True
    )
    food_array: np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]] = Field(exclude=True)
    all_snake_moves_array: np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]] = Field(
        exclude=True
    )
    center_weight_array: np.ndarray[Any, np.dtype[np.signedinteger[_8Bit]]] = Field(
        exclude=True
    )
    score: float = 0

    @classmethod
    def factory(cls, **kwargs) -> BoardState:  # type: ignore
        my_snake = kwargs["my_snake"]
        other_snakes = kwargs["other_snakes"]
        board_height = kwargs["board_height"]
        board_width = kwargs["board_width"]
        prev_state = kwargs.get("prev_state")

        if prev_state is None:
            board_array = get_board_array(
                board_width=board_width, board_height=board_height
            )
            center_weight_array = get_center_weight_array(board_array=board_array)
        else:
            board_array = prev_state.board_array
            center_weight_array = prev_state.center_weight_array

        snake_heads_at_coord_dict = get_snake_heads_at_coord(
            snakes=(my_snake, *other_snakes)
        )
        for coord, snake_heads_at_coord in snake_heads_at_coord_dict.items():
            resolve_head_collision(snake_heads_at_coord=snake_heads_at_coord)
            kwargs["food_coords"] = resolve_food_consumption(
                coord=coord,
                snake_heads_at_coord=snake_heads_at_coord,
                food_coords=kwargs["food_coords"],
            )

        if my_snake.elimination is not None or len(other_snakes) == 0:
            terminal_reason: Literal["self_eliminated", "victory"]
            score: int
            if my_snake.elimination is not None:
                terminal_reason = "self_eliminated"
                score = 0
            elif len(other_snakes) == 0:
                terminal_reason = "victory"
                score = WIN_SCORE
            else:
                raise Exception("unhandled termination reason")

            return cls(
                board_array=np.array([]),
                food_array=np.array([]),
                all_snake_moves_array=np.array([]),
                center_weight_array=np.array([]),
                is_terminal=True,
                score=score,
                terminal_reason=terminal_reason,
                **kwargs,
            )

        all_snake_bodies_array = get_all_snake_bodies_array(
            board_array=board_array, snakes=(my_snake, *other_snakes)
        )

        # TODO: resolve head collision and food consumption here

        all_snake_moves_array = get_all_snake_moves_array(
            all_snake_bodies_array=all_snake_bodies_array,
        )

        food_array = get_food_array(
            board_array=board_array, food_coords=kwargs["food_coords"]
        )

        score = get_score(
            my_snake=my_snake,
            food_array=food_array,
            center_weight_array=center_weight_array,
            all_snake_moves_array=all_snake_moves_array,
        )

        return cls(
            board_array=board_array,
            food_array=food_array,
            all_snake_moves_array=all_snake_moves_array,
            center_weight_array=center_weight_array,
            score=score + my_snake.health,
            **kwargs,
        )

    def get_my_key(self) -> tuple[int, Coord]:
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

    def get_next_health(
        self,
        next_body: tuple[Coord, ...],
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
            log.warning(
                "Health is greater than 100. Not sure how that happened.",
                snake_id=snake.id,
            )
            return 100

        return next_health

    def get_next_body(self, current_body: tuple[Coord, ...]) -> tuple[Coord, ...]:
        if current_body[0] is DEATH_COORD:
            return (current_body[0],)
        if current_body[0] in self.food_coords:
            current_body = (*current_body, current_body[-1])
        return current_body

    def is_food_consumed(self, next_body: tuple[Coord, ...]) -> bool:
        if next_body[0] in self.food_coords:
            return True
        return False

    def get_next_snake_state_for_snake_move(
        self, snake: SnakeState, move: Coord
    ) -> SnakeState:
        # TODO: Add an eliminated by object. Mirror what they're doing with board and rules
        next_body = self.get_next_body(current_body=(move, *snake.body[:-1]))
        food_consumed = self.is_food_consumed(next_body=next_body)
        next_health = self.get_next_health(
            next_body=next_body, food_consumed=food_consumed, snake=snake
        )

        if food_consumed:
            food_consumed_coords = tuple([*snake.food_consumed, next_body[0]])
        else:
            food_consumed_coords = tuple([*snake.food_consumed])

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
            latency=str(snake.latency),
            shout=snake.shout,
            is_self=snake.is_self,
            murder_count=snake.murder_count,
            food_consumed=food_consumed_coords,
            elimination=elimination,
            prev_state=snake,
        )

    def get_next_snake_states_for_snake(
        self, snake: SnakeState, index: int
    ) -> list[SnakeState]:
        _, rows, _ = self.all_snake_moves_array.shape
        if snake.elimination is not None:
            return []

        moves = [
            Coord(x=np_ind[1] - 1, y=rows - 2 - np_ind[0])
            for np_ind in np.argwhere(self.all_snake_moves_array[index] == 1)
        ]

        if len(moves) == 0:
            moves.append(DEATH_COORD)

        if (
            len(moves) > 1
            and not snake.is_self
            and self.my_snake.head.get_manhattan_distance(snake.head) > 4
        ):
            if self.turn % 2 == 1 and snake.body[0] + snake.last_move in moves:
                moves = [snake.body[0] + snake.last_move]
            else:
                moves = [
                    move
                    for move in moves
                    if self.my_snake.head.get_manhattan_distance(move)
                    < self.my_snake.head.get_manhattan_distance(snake.head)
                ]

        return [
            self.get_next_snake_state_for_snake_move(snake=snake, move=move)
            for move in moves
        ]

    def populate_next_boards(self) -> Generator[BoardState, None, None]:
        if self.is_terminal:
            return
        my_snake_next_states = self.get_next_snake_states_for_snake(
            snake=self.my_snake, index=0
        )
        other_snakes_next_states = [
            other_snake_next_state
            for other_snake_next_state in [
                self.get_next_snake_states_for_snake(snake=snake, index=index + 1)
                for index, snake in enumerate(
                    [snake for snake in self.other_snakes if snake.elimination is None]
                )
            ]
            if len(other_snake_next_state) > 0
        ]
        all_potential_snake_states: tuple[list[SnakeState]] = product(  # type: ignore
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
                other_snakes=tuple(
                    snake.model_copy() for snake in potential_snake_states[1:]
                ),
                hazard_damage_rate=self.hazard_damage_rate,
                prev_state=self,
            )
            self.next_boards.append(potential_board)
            self.score = sum([board.score for board in self.next_boards]) / len(
                self.next_boards
            )
            yield potential_board
        return

    def get_snake_state_payload(
        self,
        snake_defs: dict[str, SnakeDef],
        snake_id: str,
    ) -> dict:
        snakes = [
            snake
            for snake in [self.my_snake, *self.other_snakes]
            if snake.id == snake_id
        ]
        if len(snakes) == 0:
            return {
                "id": snake_id,
                "name": snake_defs[snake_id].name,
                "health": 0,
                "body": [],
                "latency": "0",
                "length": 0,
                "customizations": snake_defs[snake_id].customizations.model_dump(),
                "elimination": Elimination(cause="unknown", by="unknown"),
            }
        snake = snakes[0]

        return {
            "id": snake.id,
            "name": snake_defs[snake.id].name,
            "health": snake.health,
            "body": [coord.as_dict for coord in snake.body],
            "latency": str(snake.latency),
            "head": snake.head.as_dict,
            "length": snake.length,
            "customizations": snake_defs[snake.id].customizations.model_dump(),
            "elimination": snake.elimination.model_dump()
            if snake.elimination is not None
            else None,
        }

    def get_snake_payload(
        self,
        snake_defs: dict[str, SnakeDef],
        snake_id: str,
    ) -> dict:
        snake_state_payload = self.get_snake_state_payload(
            snake_defs=snake_defs, snake_id=snake_id
        )
        snake_state_payload.pop("elimination")
        snake_state_payload["shout"] = None
        return snake_state_payload

    def get_board_payload(self, snake_defs: dict[str, SnakeDef], game: Game) -> dict:
        return {
            "game": game.model_dump(),
            "turn": self.turn,
            "board": {
                "height": self.board_height,
                "width": self.board_width,
                "food": [coord.as_dict for coord in self.food_coords],
                "hazards": [coord.as_dict for coord in self.hazard_coords],
                "snakes": [
                    self.get_snake_state_payload(
                        snake_id=snake.id, snake_defs=snake_defs
                    )
                    for snake in [self.my_snake, *self.other_snakes]
                ],
            },
            "you": self.get_snake_state_payload(
                snake_id=self.my_snake.id, snake_defs=snake_defs
            ),
            "terminalReason": self.terminal_reason,
            "score": self.score,
            "descendents": [
                next_board.get_board_payload(snake_defs=snake_defs, game=game)
                for next_board in self.next_boards
            ],
        }

    def get_move_request(self, snake_defs: dict[str, SnakeDef], game: Game) -> dict:
        return {
            "game": game.model_dump(),
            "turn": self.turn,
            "board": {
                "height": self.board_height,
                "width": self.board_width,
                "food": [coord.as_dict for coord in self.food_coords],
                "hazards": [coord.as_dict for coord in self.hazard_coords],
                "snakes": [
                    self.get_snake_payload(snake_id=snake.id, snake_defs=snake_defs)
                    for snake in [self.my_snake, *self.other_snakes]
                ],
            },
            "you": self.get_snake_payload(
                snake_id=self.my_snake.id, snake_defs=snake_defs
            ),
        }

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BoardState):
            return self.model_dump() == other.model_dump()
        return super().__eq__(other)

    def is_inferior_to(self, other: BoardState) -> bool:
        return (
            self.my_snake.length <= other.my_snake.length
            and self.my_snake.murder_count <= other.my_snake.murder_count
            and self.my_snake.health <= other.my_snake.health
            and self.score <= other.score
            and any(
                [
                    self.my_snake.length < other.my_snake.length,
                    self.my_snake.murder_count < other.my_snake.murder_count,
                    self.my_snake.health < other.my_snake.health,
                    self.score < other.score,
                ]
            )
        )

    def is_superior_to(self, other: BoardState) -> bool:
        return (
            self.my_snake.length >= other.my_snake.length
            and self.my_snake.murder_count >= other.my_snake.murder_count
            and self.my_snake.health >= other.my_snake.health
            and self.score >= other.score
            and any(
                [
                    self.my_snake.length > other.my_snake.length,
                    self.my_snake.murder_count > other.my_snake.murder_count,
                    self.my_snake.health > other.my_snake.health,
                    self.score > other.score,
                ]
            )
        )
