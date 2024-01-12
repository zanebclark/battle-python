from __future__ import annotations

from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import NonNegativeInt

from battle_python.BoardState import BoardState
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


class GameState(BaseModel):
    game: Game
    board_height: NonNegativeInt
    board_width: NonNegativeInt
    current_turn: NonNegativeInt
    turns: dict[int, list[BoardState]]
    snake_defs: dict[str, SnakeDef]

    # noinspection PyNestedDecorators
    @classmethod
    def from_payload(cls, payload: dict) -> GameState:
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
                health=snake["health"],
                body=snake["body"],
                head=snake["head"],
                length=snake["length"],
                latency=snake["latency"],
                shout=snake["shout"],
                is_self=snake["id"] == my_snake_id,
            )
            for snake in payload["board"]["snakes"]
        ]

        board = BoardState(
            turn=payload["turn"],
            board_width=payload["board"]["width"],
            board_height=payload["board"]["height"],
            food_coords=payload["board"]["food"],
            hazard_coords=payload["board"]["hazards"],
            snake_states=snake_states,
            hazard_damage_rate=game.ruleset.settings.hazardDamagePerTurn,
        )

        return GameState(
            game=game,
            board_width=payload["board"]["width"],
            board_height=payload["board"]["height"],
            current_turn=payload["turn"],
            turns={0: [board]},
            snake_defs=snake_defs,
        )
