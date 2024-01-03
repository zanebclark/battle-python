import random
from typing import Dict, List, Optional
from dataclasses import dataclass

from battle_python.BattlesnakeTypes import Battlesnake, Coord, GameState, MoveDirection


@dataclass(frozen=True)
class BattlesnakeStub:
    id: str
    section: int
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
    you: Battlesnake

    def get_safe_moves(self, snake_head_coord: Coord) -> Dict[Coord, MoveDirection]:
        moves: Dict[Coord, MoveDirection] = {
            Coord(snake_head_coord.x, snake_head_coord.y + 1): "up",
            Coord(snake_head_coord.x, snake_head_coord.y - 1): "down",
            Coord(snake_head_coord.x - 1, snake_head_coord.y): "left",
            Coord(snake_head_coord.x + 1, snake_head_coord.y): "right",
        }
        for coord in list(moves.keys()):
            # Avoid moving out of bounds
            if coord not in self.cells:
                del moves[coord]
                continue

            coord_state = self.cells[coord]

            # Avoid colliding with any snake (including yourself)
            for other_snake, prob in coord_state.snake_prob.items():
                # Avoid body collisions altogether
                # This will also exclude your neck
                if other_snake.section >= 1:
                    del moves[coord]
                    continue

                # Allow head collisions if longer
                if prob >= 33 and other_snake.length >= self.you.length:
                    del moves[coord]

        return moves


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
                    section=snake.body.index(coord),
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
                    cells=cells, turn=gs.turn, snakes=gs.board.snakes, you=gs.you
                )
            ],
        )

    def next_frame(self):
        # TODO: Has the food been eaten?
        # TODO: Where could the snakes move?
        # TODO: Hazard progression?
        current_frame = self.frames[-1]
        for snake in current_frame.snakes:
            safe_moves = current_frame.get_safe_moves(snake_head_coord=snake.head)
            move_prob = round(100 / len(safe_moves.keys()))

        # for snake in current_frame.snakes.values():

        #     if

        your_snake = current_frame.snakes[self.your_battlesnake_id]

        # Append the last move
        your_snake.body.insert(0, move)

        # If you ate food on the previous round, your health will be at 100 and your tail won't be popped this round
        if your_snake.health != 100:
            your_snake.body.pop()

        your_snake = None
        for coord in self.coords:
            pass
        # self.frames.append(next_gs)


def get_next_move(gs: GameState):
    game = Game.from_game_state(gs=gs)
    moves = game.frames[0].get_safe_moves(game.frames[0].you.head)

    # TODO: Implement some sort of yield to return a move here

    return random.choice(list(moves.values()))
