from __future__ import annotations

from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import NonNegativeInt

from battle_python.EnrichedBoard import EnrichedBoard
from battle_python.SnakeState import SnakeState
from battle_python.api_types import (
    FrozenBaseModel,
    SnakeCustomizations,
    Coord,
    Game,
)

DEATH = Coord(x=1000, y=1000)


class SnakeDef(FrozenBaseModel):
    id: str
    name: str
    customizations: SnakeCustomizations
    is_self: bool = False


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
