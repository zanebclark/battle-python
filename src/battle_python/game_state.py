from __future__ import annotations

from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import NonNegativeInt

from battle_python.api_types import (
    FrozenBaseModel,
    SnakeCustomizations,
    Coord,
    Game,
)


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


class SnakeState(FrozenBaseModel):
    snake_id: str
    probability: float
    health: NonNegativeInt
    body: list[Coord]
    head: Coord
    length: NonNegativeInt
    latency: NonNegativeInt | None = None
    shout: str | None = None
    is_self: bool = False
    prev_state: SnakeState | None = None

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

    def get_self_evading_moves(
        self,
        board_width: NonNegativeInt,
        board_height: NonNegativeInt,
    ) -> list[Coord]:
        coords = get_legal_adjacent_coords(
            board_width=board_width, board_height=board_height, coord=self.head
        )
        return [coord for coord in coords if not self.is_collision(coord=coord)]

    def get_next_body_sans_head(self) -> list[Coord]:
        next_body_sans_head: list[Coord] = []
        for current_body_index, coord in enumerate(self.body):
            if coord == self.body[-1] and not self.is_growing():
                continue
            next_body_sans_head.append(coord)

        return next_body_sans_head

    def get_next_states(
        self,
        board_width: NonNegativeInt,
        board_height: NonNegativeInt,
    ) -> list[SnakeState]:
        safe_moves = self.get_self_evading_moves(
            board_width=board_width, board_height=board_height
        )
        option_count = float(len(safe_moves))

        if option_count == 0:
            return []  # TODO: How do I reflect that the snake will die?

        next_body_sans_head: list[Coord] = self.get_next_body_sans_head()

        safe_snake_coords = [
            SnakeState(
                snake_id=self.snake_id,
                probability=self.probability / option_count,
                health=self.health - 1,
                body=[coord, *next_body_sans_head],
                head=coord,
                length=self.length,
                is_self=self.is_self,
                prev_state=self,
            )
            for coord in safe_moves
        ]

        return safe_snake_coords


class EnrichedBoard(FrozenBaseModel):
    turn: NonNegativeInt
    food: list[Coord]
    hazards: list[Coord]
    snake_states: list[SnakeState]


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
                probability=100,
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
            turn=payload["turn"],
            food=payload["board"]["food"],
            hazards=payload["board"]["hazards"],
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
