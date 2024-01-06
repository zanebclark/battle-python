from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Literal

Direction = Literal["up", "down", "left", "right"]

GameSource = Literal["tournament", "league", "arena", "challenge", "custom"]


@dataclass(frozen=True)
class BattlesnakeCustomizations:
    color: str | None
    head: str | None
    tail: str | None


@dataclass(frozen=True, kw_only=True)
class BattlesnakeDetails(BattlesnakeCustomizations):
    author: str | None
    version: str | None
    apiversion: Literal["1"] = "1"


@dataclass(frozen=True)
class Ruleset:
    name: str
    version: str
    settings: dict


@dataclass(frozen=True)
class Game:
    id: str
    ruleset: Ruleset
    map: str
    timeout: int
    source: GameSource


@dataclass(frozen=True)
class Coord:
    x: int
    y: int

    def get_legal_moves(
        self, board_width: int, board_height: int
    ) -> dict[Coord, Direction]:
        moves = self.get_potential_moves()
        for coord in list(moves.keys()):
            if (
                coord.x < 0
                or coord.x > board_width - 1
                or coord.y < 0
                or coord.y > board_height - 1
            ):
                del moves[coord]
                continue

        return moves

    def get_potential_moves(self) -> dict[Coord, Direction]:
        moves: dict[Coord, Direction] = {
            Coord(self.x, self.y + 1): "up",
            Coord(self.x, self.y - 1): "down",
            Coord(self.x - 1, self.y): "left",
            Coord(self.x + 1, self.y): "right",
        }
        return moves


def get_board_coords(board_width: int, board_height: int) -> list[Coord]:
    coords: list[Coord] = [
        Coord(x=x, y=y) for x, y in product(range(board_width), range(board_height))
    ]
    return coords


@dataclass(frozen=True)
class MoveResponse:
    move: Direction
    shout: str | None = None


# TODO: This might not be true. Per the rules, consuming food increases the snake's length
# before the next /move request is sent. I assume that that request would list the snake's
# increased length. That's it! The length increases, but the count of the coordinates stays
# the same. I need to review some logs to see if this is the case.
#
# The tail might not be there. If the snake just ate food (health = 100), it will remain.
# The snake's health will be at 100 at the beginning of the game, so omit that condition.
def is_snake_growing(turn: int, health: int) -> bool:
    if turn == 0:
        return False
    return health == 100


def get_body_evading_moves(
    body_coords: list[Coord],
    snake_growing: bool,
    board_width: int,
    board_height: int,
) -> dict[Coord, Direction]:
    moves = body_coords[0].get_legal_moves(
        board_width=board_width, board_height=board_height
    )

    for coord in list(moves.keys()):
        if coord in body_coords[0:-1]:  # Avoid self collision.
            del moves[coord]
            continue

        # Avoid your tail if it won't move
        if coord == body_coords[-1] and snake_growing:
            del moves[coord]
            continue

    return moves


@dataclass
class Spam:
    probability: float
    body_index: int = None
    direction: Direction | None = None


def get_coord_prob_dict(
    state_prob: float,
    body_coords: list[Coord],
    health: int,
    turn: int,
    board_width: int,
    board_height: int,
) -> dict[Coord, Spam]:
    coord_prob_dict: dict[Coord, Spam] = {}

    snake_growing = is_snake_growing(turn=turn, health=health)

    for current_body_index, coord in enumerate(body_coords):
        body_index = current_body_index + 1
        if coord == body_coords[-1] and not snake_growing:
            continue

        coord_prob_dict[coord] = Spam(probability=state_prob, body_index=body_index)

    safe_moves = get_body_evading_moves(
        body_coords=body_coords,
        snake_growing=snake_growing,
        board_width=board_width,
        board_height=board_height,
    )
    options = float(len(safe_moves.keys()))
    if options == 0:
        return coord_prob_dict
    prob = state_prob / float(len(safe_moves.keys()))
    for coord, direction in safe_moves.items():
        if coord_prob_dict.get(coord) is None:
            coord_prob_dict[coord] = Spam(
                probability=prob, body_index=0, direction=direction
            )
        else:
            # Ouroboros
            coord_prob_dict[coord].probability += prob

    return coord_prob_dict


@dataclass
class Battlesnake:
    id: str
    name: str
    health: int
    body: list[Coord]
    latency: str
    head: Coord
    length: int
    shout: str
    customizations: BattlesnakeCustomizations
    is_self: bool = False
    turn_prob: dict[int, dict[Coord, object]] = field(default_factory=dict)

    def delete_from_turn_prob(self, turn: int, coord: Coord) -> None:
        option_count = len(
            [val for val in self.turn_prob[turn].values() if val.body_index == 0]
        )
        if option_count == 1:
            # TODO: Is there something better to do here?
            return

        del self.turn_prob[turn][coord]
        remaining_option_count = len(
            [val for val in self.turn_prob[turn].values() if val.body_index == 0]
        )
        new_prob = float(100 / remaining_option_count)
        for remaining_option in self.turn_prob[turn].values():
            if remaining_option.body_index != 0:
                continue
            remaining_option.probability = new_prob

    def get_next_turn_length(self, turn: int) -> int:
        next_turn_length = self.length
        if is_snake_growing(turn=turn, health=self.health):
            next_turn_length += 1
        return next_turn_length


@dataclass
class Board:
    height: int
    width: int
    food: list[Coord]
    hazards: list[Coord]
    snakes: list[Battlesnake]
    snake_dict: dict[str, Battlesnake] = field(default_factory=dict)

    def mark_your_snake(self, your_snake_id: str):
        for snake in self.snakes:
            if snake.id == your_snake_id:
                snake.is_self = True
                return

    def __post_init__(self):
        for snake in self.snakes:
            self.snake_dict[snake.id] = snake


@dataclass
class GameState:
    game: Game
    turn: int
    board: Board
    you: Battlesnake

    def __post_init__(self):
        self.board.mark_your_snake(your_snake_id=self.you.id)
