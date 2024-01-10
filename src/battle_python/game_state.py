from __future__ import annotations

from collections import defaultdict
import random

from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import NonNegativeInt

from battle_python.api_types import (
    FrozenBaseModel,
    SnakeCustomizations,
    Coord,
    Game,
)

DEATH = Coord(x=1000, y=1000)


def get_legal_adjacent_coords(
    coord: Coord,
    board_width: NonNegativeInt,
    board_height: NonNegativeInt,
) -> list[Coord]:
    adj_coords = coord.get_adjacent()
    return [
        coord
        for coord in adj_coords
        if 0 <= coord.x <= board_width - 1 and 0 <= coord.y <= board_height - 1
    ]


class SnakeDef(FrozenBaseModel):
    id: str
    name: str
    customizations: SnakeCustomizations
    is_self: bool = False


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

    def get_reasonable_moves(
        self,
        board_width: NonNegativeInt,
        board_height: NonNegativeInt,
        snake_states: list[SnakeState],
    ) -> list[Coord]:
        coords = get_legal_adjacent_coords(
            board_width=board_width, board_height=board_height, coord=self.head
        )

        snake_body_coords = [
            coord
            for snake in snake_states
            for coord in snake.body[:-1]
            if snake.state_prob == 1  # TODO: Make this configurable
        ]

        potential_snake_head_coords = [
            coord
            for snake in snake_states
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
        board_width: NonNegativeInt,
        board_height: NonNegativeInt,
        snake_states: list[SnakeState],
    ) -> list[SnakeState]:
        reasonable_moves = self.get_reasonable_moves(
            board_width=board_width,
            board_height=board_height,
            snake_states=snake_states,
        )
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


class EnrichedBoard(FrozenBaseModel):
    turn: NonNegativeInt
    board_height: NonNegativeInt
    board_width: NonNegativeInt
    food_prob: dict[Coord, float]
    hazard_prob: dict[Coord, float]
    snake_states: list[SnakeState]

    def get_next_board(self) -> EnrichedBoard:
        next_food_prob: dict[Coord, float] = {**self.food_prob}
        next_snake_states = [
            state
            for next_states in self.snake_states
            for state in next_states.get_next_states(
                board_width=self.board_width,
                board_height=self.board_height,
                snake_states=self.snake_states,
            )
        ]

        heads_at_coord: dict[Coord, list[SnakeState]] = defaultdict(list)
        for next_snake_state in next_snake_states:
            heads_at_coord[next_snake_state.head].append(next_snake_state)

        # Resolve head collisions and food_prob consumption
        for coord, snake_states in heads_at_coord.items():
            # Resolve head collisions
            if len(snake_states) > 1:
                snake_states.sort(key=lambda snake: snake.length)
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


class EnrichedGameState(BaseModel):
    game: Game
    board_height: NonNegativeInt
    board_width: NonNegativeInt
    current_turn: NonNegativeInt
    turns: list[EnrichedBoard]
    snake_defs: dict[str, SnakeDef]

    # noinspection PyNestedDecorators
    @classmethod
    def from_payload(cls, payload: dict) -> EnrichedGameState:
        game = Game(**payload["game"])

        my_snake_id = payload["you"]["id"]

        snake_defs = {
            snake["id"]: SnakeDef(
                id=snake["id"],
                name=snake["name"],
                customizations=snake["customizations"],
                is_self=snake["id"] == my_snake_id,
            )
            for snake in payload["board"]["snakes"]
        }

        snake_states: list[SnakeState] = [
            SnakeState(
                snake_id=snake["id"],
                state_prob=1,
                death_prob=0,
                food_prob=0,
                murder_prob=0,
                health=snake["health"],
                body=snake["body"],
                latency=snake["latency"],
                head=snake["head"],
                length=snake["length"],
                shout=snake["shout"],
                is_self=snake["id"] == my_snake_id,
            )
            for snake in payload["board"]["snakes"]
        ]

        board = EnrichedBoard(
            board_width=payload["board"]["width"],
            board_height=payload["board"]["height"],
            turn=payload["turn"],
            food_prob={
                Coord(x=coord["x"], y=coord["y"]): 1
                for coord in payload["board"]["food"]
            },
            hazard_prob={
                Coord(x=coord["x"], y=coord["y"]): 1
                for coord in payload["board"]["hazards"]
            },
            snake_states=snake_states,
        )

        return EnrichedGameState(
            game=game,
            board_width=payload["board"]["width"],
            board_height=payload["board"]["height"],
            current_turn=payload["turn"],
            turns=[board],
            snake_defs=snake_defs,
        )
