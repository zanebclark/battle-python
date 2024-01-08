from __future__ import annotations

from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import NonNegativeInt

from battle_python.api_types import (
    FrozenBaseModel,
    SnakeCustomizations,
    Coord,
    Game,
    Direction,
)


class SnakeDef(FrozenBaseModel):
    id: str
    name: str
    customizations: SnakeCustomizations
    is_self: bool = False


class SnakeState(FrozenBaseModel):
    health: NonNegativeInt
    body: list[Coord]
    latency: str
    head: Coord
    length: NonNegativeInt
    shout: str | None
    is_self: bool = False

    def is_growing(self):
        """
        If the snake consumed food on the previous round, the last two coordinates of its body will be equal.
        The snake's tail won't move on the next round.
        :return:
        """
        return self.body[-1] == self.body[-2]

    def is_collision(self, coord: Coord) -> bool:
        # Avoid self collision.
        if coord in self.body[0:-1]:
            return True

        # Avoid your tail if it won't move
        if coord == self.body[-1] and self.is_growing():
            return True

        return False


class Spam(FrozenBaseModel):
    probability: float
    body_index: int = None
    direction: Direction | None = None


class EnrichedBoard(FrozenBaseModel):
    height: NonNegativeInt
    width: NonNegativeInt
    food: list[Coord]
    hazards: list[Coord]
    snake_states: dict[str, SnakeState]

    def is_legal(self, coord: Coord):
        return 0 <= coord.x <= self.width - 1 and 0 <= coord.y <= self.height - 1

    def get_legal_adjacent_coords(self, coord: Coord) -> list[Coord]:
        adj_coords = coord.get_adjacent()
        return [coord for coord in adj_coords if self.is_legal(coord)]

    def get_body_evading_moves(self, snake_id) -> list[Coord]:
        snake = self.snake_states[snake_id]
        coords = self.get_legal_adjacent_coords(snake.head)
        return [coord for coord in coords if not snake.is_collision(coord=coord)]

    def get_coord_prob_dict(
        self,
        snake_id: str,
        state_prob: float,
    ):
        coord_prob_dict: dict[Coord, Spam] = {}
        snake = self.snake_states[snake_id]

        for current_body_index, coord in enumerate(snake.body):
            body_index = current_body_index + 1
            if coord == snake.body[-1] and not snake.is_growing():
                continue

            coord_prob_dict[coord] = Spam(
                probability=state_prob,
                body_index=body_index,
            )

        safe_moves = self.get_body_evading_moves(snake_id=snake_id)
        options = float(len(safe_moves))

        if options == 0:
            return coord_prob_dict

        prob = state_prob / options
        for coord in safe_moves:
            coord_prob_dict[coord] = Spam(
                probability=prob,
                body_index=0,
            )

        return coord_prob_dict


class EnrichedGameState(BaseModel):
    game: Game
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

        snake_states = {
            snake["id"]: SnakeState(
                health=snake["health"],
                body=snake["body"],
                latency=snake["latency"],
                head=snake["head"],
                length=snake["length"],
                shout=snake["shout"],
                is_self=snake["id"] == my_snake_id,
            )
            for snake in payload["board"]["snakes"]
        }

        board = EnrichedBoard(
            height=payload["board"]["height"],
            width=payload["board"]["width"],
            food=payload["board"]["food"],
            hazards=payload["board"]["hazards"],
            snake_states=snake_states,
        )

        return EnrichedGameState(
            game=game,
            current_turn=payload["turn"],
            turns=[board],
            snake_defs=snake_defs,
        )
