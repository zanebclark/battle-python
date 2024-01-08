from __future__ import annotations

from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import NonNegativeInt

from battle_python.api_types import (
    FrozenBaseModel,
    SnakeCustomizations,
    Coord,
    Game,
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
