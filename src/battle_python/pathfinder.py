import random
from typing import Dict, List, Optional
from dataclasses import dataclass

from battle_python.BattlesnakeTypes import Battlesnake, Coord, GameState


@dataclass(frozen=True)
class CoordState(Coord):
    is_food: bool
    is_hazard: bool
    snakes: List[Battlesnake]


@dataclass(frozen=True)
class BoardState:
    turn: int
    cells: Dict[Coord, CoordState]


@dataclass
class Game:
    height: int
    width: int
    coords: List[Coord]
    frames: List[BoardState]

    @staticmethod
    def get_coords(width: int, height: int) -> List[Coord]:
        coords: List[Coord] = []
        for x in range(width + 1):
            for y in range(height + 1):
                coords.append(Coord(x=x, y=y))
        return coords

    @classmethod
    def from_game_state(cls, gs: GameState):
        cells: Dict[Coord, CoordState] = {}

        coords = cls.get_coords(width=gs.board.width, height=gs.board.height)
        for coord in coords:
            is_food = coord in gs.board.food
            is_hazard = coord in gs.board.hazards
            snakes = [snake for snake in gs.board.snakes if coord in snake.body]

            cells[coord] = CoordState(
                x=coord.x,
                y=coord.y,
                is_food=is_food,
                is_hazard=is_hazard,
                snakes=snakes,
            )

        return cls(
            height=gs.board.height,
            width=gs.board.width,
            coords=coords,
            frames=[BoardState(cells=cells, turn=gs.turn)],
        )

    # def next_frame(self):
    #     # TODO: Has the food been eaten?
    #     # TODO: Where could the snakes move?
    #     # TODO: Hazard progression?
    #     current_frame = self.frames[-1]
    #     for coord in self.coords:
    #         pass
    #     self.frames.append(next_gs)


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
        if coord_state.snakes:
            del moves[coord]
    return random.choice(list(moves.values()))
