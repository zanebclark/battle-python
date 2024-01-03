import random
from typing import Dict, List, Optional
from dataclasses import dataclass

from battle_python.BattlesnakeTypes import Battlesnake, Coord, GameState


@dataclass(frozen=True)
class BattlesnakeStub:
    id: str
    health: str
    latency: str
    length: int


@dataclass(frozen=True)
class CoordState(Coord):
    is_food_prob: int
    is_hazard_prob: int
    snake_prob: Dict[BattlesnakeStub, int]


@dataclass(frozen=True)
class BoardState:
    turn: int
    snakes: List[Battlesnake]
    cells: Dict[Coord, CoordState]


@dataclass
class Game:
    height: int
    width: int
    coords: List[Coord]
    frames: List[BoardState]
    your_battlesnake_id: str

    @staticmethod
    def get_coords(width: int, height: int) -> List[Coord]:
        coords: List[Coord] = []
        for x in range(width):
            for y in range(height):
                coords.append(Coord(x=x, y=y))
        return coords

    @classmethod
    def from_game_state(cls, gs: GameState):
        cells: Dict[Coord, CoordState] = {}

        coords = cls.get_coords(width=gs.board.width, height=gs.board.height)
        for coord in coords:
            is_food_prob = 100 if coord in gs.board.food else 0
            is_hazard_prob = 100 if coord in gs.board.hazards else 0
            snake_prob = {
                BattlesnakeStub(
                    id=snake.id,
                    health=snake.health,
                    latency=snake.latency,
                    length=snake.length,
                ): 100
                for snake in gs.board.snakes
                if coord in snake.body
            }

            cells[coord] = CoordState(
                x=coord.x,
                y=coord.y,
                is_food_prob=is_food_prob,
                is_hazard_prob=is_hazard_prob,
                snake_prob=snake_prob,
            )

        return cls(
            your_battlesnake_id=gs.you.id,
            height=gs.board.height,
            width=gs.board.width,
            coords=coords,
            frames=[
                BoardState(
                    cells=cells,
                    turn=gs.turn,
                    snakes=[snake for snake in gs.board.snakes],
                )
            ],
        )

    def next_frame(self, move: Coord):
        # TODO: Has the food been eaten?
        # TODO: Where could the snakes move?
        # TODO: Hazard progression?
        current_frame = self.frames[-1]
        for coord in self.coords:
            pass
        # self.frames.append(next_gs)


def get_next_move(gs: GameState):
    game = Game.from_game_state(gs=gs)
    moves = {
        Coord(gs.you.head.x, gs.you.head.y + 1): "up",
        Coord(gs.you.head.x, gs.you.head.y - 1): "down",
        Coord(gs.you.head.x - 1, gs.you.head.y): "left",
        Coord(gs.you.head.x + 1, gs.you.head.y): "right",
    }
    for coord in list(moves.keys()):
        # Avoid moving out of bounds
        if coord not in game.frames[0].cells:
            del moves[coord]
            continue
        coord_state = game.frames[0].cells[coord]
        # Avoid colliding with any snake (including yourself)
        if coord_state.snake_prob:
            del moves[coord]

        # TODO: Implement some sort of yield to return a move here

    return random.choice(list(moves.values()))
