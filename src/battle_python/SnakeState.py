from __future__ import annotations
from typing import TYPE_CHECKING

from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import NonNegativeInt

if TYPE_CHECKING:
    from battle_python.EnrichedBoard import EnrichedBoard
from battle_python.api_types import Coord

DEATH = Coord(x=1000, y=1000)


class SnakeState(BaseModel):
    snake_id: str
    state_prob: float
    death_prob: float
    food_prob: float
    murder_prob: float
    health: NonNegativeInt
    body: list[Coord]
    head: Coord
    length: NonNegativeInt
    latency: NonNegativeInt | None = None
    shout: str | None = None
    is_self: bool = False
    prev_state: SnakeState | None = None

    def get_reasonable_moves(self, board: EnrichedBoard) -> list[Coord]:
        coords = board.get_legal_adjacent_coords(coord=self.head)

        snake_body_coords = [
            coord
            for snake in board.snake_states
            for coord in snake.body[:-1]
            if snake.state_prob == 1  # TODO: Make this configurable
        ]

        potential_snake_head_coords = [
            coord
            for snake in board.snake_states
            for coord in snake.head.get_adjacent()
            if not snake.is_self
            and snake.length >= self.length
            and snake.state_prob >= float(1 / 3)  # TODO: Make this configurable
        ]

        return [
            coord
            for coord in coords
            if coord not in snake_body_coords
            and coord not in potential_snake_head_coords
        ]

    def get_next_states(
        self,
        board: EnrichedBoard,
    ) -> list[SnakeState]:
        reasonable_moves = self.get_reasonable_moves(board=board)
        option_count = float(len(reasonable_moves))

        if option_count == 0:
            reasonable_moves = [DEATH]
            option_count = 1

        safe_snake_coords = [
            SnakeState(
                snake_id=self.snake_id,
                state_prob=self.state_prob / option_count,
                death_prob=self.death_prob if coord is not DEATH else 1,
                food_prob=self.food_prob,
                murder_prob=self.murder_prob,
                health=self.health - 1,  # TODO: Address hazard zones
                body=[coord, *self.body[:-1]],
                head=coord,
                length=self.length,
                is_self=self.is_self,
                prev_state=self,
            )
            for coord in reasonable_moves
        ]

        return safe_snake_coords
