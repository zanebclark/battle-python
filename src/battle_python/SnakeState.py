from __future__ import annotations

import numpy as np
import numpy.typing as npt
import numpy.ma as ma
from typing import Literal

from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import NonNegativeInt, Field, ConfigDict

from battle_python.api_types import Coord
from battle_python.constants import DEATH_COORD, UNEXPLORED_VALUE
from aws_lambda_powertools import Logger

from battle_python.utils import get_aligned_masked_array

logger = Logger()


class Elimination(BaseModel):
    cause: Literal[
        "snake-collision",
        "snake-self-collision",
        "out-of-health",
        "hazard",
        "head-collision",
        "wall-collision",
    ]
    by: str | None = None


class SnakeState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str
    health: NonNegativeInt
    body: tuple[Coord, ...]
    head: Coord
    length: NonNegativeInt
    latency: NonNegativeInt
    shout: str | None = None
    is_self: bool = False
    murder_count: int = 0
    food_consumed: tuple[Coord, ...] = Field(default_factory=tuple)
    elimination: Elimination | None = None
    prev_state: SnakeState | None = Field(default=None, exclude=True)
    body_array: npt.NDArray[np.int_] = Field(exclude=True)
    moves_array: npt.NDArray[np.int_] | None = Field(default=None, exclude=True)
    moves_exhausted: bool = False

    @property
    def last_move(self):
        return Coord(
            x=(self.body[0].x - self.body[1].x), y=self.body[0].y - self.body[1].y
        )

    @staticmethod
    def get_body_array(
        board_array: npt.NDArray[np.int_], body: tuple[Coord, ...]
    ) -> npt.NDArray[np.int_]:
        body_array = np.copy(board_array, subok=True)
        if DEATH_COORD in body:
            return board_array
        rows, _ = body_array.shape
        body_array[
            [
                (rows - 2 - coord.y) for coord in body
            ],  # Rows (y-axis) are the first element. Indexing is top to bottom
            [
                coord.x + 1 for coord in body
            ],  # Rows (x-axis) are the second element. +1 for the pad
        ] = np.arange(
            len(body)
        )  # Set the value equal to the index of the snake body

        # print("body_array")
        # print(get_aligned_masked_array(body_array))

        return body_array

    @classmethod
    def factory(cls, board_array: npt.NDArray[np.int_], **kwargs) -> SnakeState:
        body: tuple[Coord, ...] = kwargs["body"]
        body_array = cls.get_body_array(board_array=board_array, body=body)
        return cls(body_array=body_array, **kwargs)

    def set_moves_array(self, all_snake_bodies_array: npt.NDArray[np.int_]) -> None:
        moves_array = ma.masked_array(
            np.array(all_snake_bodies_array, copy=True),
            mask=(all_snake_bodies_array >= 0),
        )
        moves_array[moves_array == -1] = UNEXPLORED_VALUE

        rows, _ = moves_array.shape
        # Set the snake's head as 0
        # The first element references rows (y axis). The second argument references columns (x axis)
        # Rows are indexed from top to bottom. Subtract y coord from rows to account for this
        # Subtract 2 to account for board buffer rows on top and bottom
        # Add 1 to x to account for left-most board buffer
        moves_array[rows - 2 - self.head.y][self.head.x + 1] = 0

        # print("moves_array")
        # print(get_aligned_masked_array(moves_array))

        self.moves_array = moves_array

    def iterate_moves_array(self, move: int) -> None:
        masked_moves_array = ma.masked_where(
            np.logical_and(
                self.moves_array != UNEXPLORED_VALUE,
                self.moves_array != move,
            ),
            self.moves_array,
            copy=False,
        )
        masked_moves_array.harden_mask()

        # print("masked_moves_array")
        # print(get_aligned_masked_array(masked_moves_array, indexed_axes=False))

        # Get indices of all Von Neumann Neighbors of elements where element == current move
        neighbors = [
            ind + shift
            for shift in [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for ind in np.argwhere(self.moves_array == move)
        ]

        if len(neighbors) == 0:
            self.moves_exhausted = True
            return

        masked_moves_array[
            [ind[0] for ind in neighbors], [ind[1] for ind in neighbors]
        ] = (move + 1)

        # print("self.moves_array")
        # print(get_aligned_masked_array(self.moves_array, indexed_axes=False))

    def test_equals(self, other: SnakeState) -> bool:
        return self.model_dump() == other.model_dump()
