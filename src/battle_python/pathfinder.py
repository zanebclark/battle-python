from itertools import groupby, product
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
    prob_dict: Dict[str, int]


def get_board_coords(board_width: int, board_height: int) -> List[Coord]:
    coords: List[Coord] = [
        Coord(x=x, y=y) for x, y in product(range(board_width), range(board_height))
    ]
    return coords


def get_combined_coord_prob_dict(
    snakes: List[Battlesnake], turn: int, board_width: int, board_height: int
) -> Dict[Coord, Dict[str, int]]:
    coord_prob_dicts: List[Dict[Coord, Dict[str, int]]] = [
        snake.get_coord_prob_dict(
            turn=turn, board_width=board_width, board_height=board_height
        )
        for snake in snakes
    ]
    return {
        coord: prob_dict
        for coord_prob_dict in coord_prob_dicts
        for coord, prob_dict in coord_prob_dict.items()
    }


@dataclass(frozen=True)
class BoardState:
    turn: int
    snakes: List[Battlesnake]
    cells: Dict[Coord, CoordState]

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

    @classmethod
    def from_game_state(cls, gs: GameState, coords: List[Coord]):
        cells: Dict[Coord, CoordState] = {}
        turn = gs.turn
        snakes = gs.board.snakes

        coord_prob_dict = get_combined_coord_prob_dict(
            snakes=snakes,
            turn=turn,
            board_height=gs.board.height,
            board_width=gs.board.width,
        )

        for coord in coords:
            is_food_prob = 100 if coord in gs.board.food else 0
            is_hazard_prob = 100 if coord in gs.board.hazards else 0
            prob_dict = coord_prob_dict.get(coord)

            cells[coord] = CoordState(
                x=coord.x,
                y=coord.y,
                is_food_prob=is_food_prob,
                is_hazard_prob=is_hazard_prob,
                prob_dict=prob_dict,
            )

        return cls(
            turn=turn,
            snakes=snakes,
            cells=cells,
        )


@dataclass
class Game:
    board_height: int
    board_width: int
    coords: List[Coord]
    frames: List[BoardState]

    @classmethod
    def from_game_state(cls, gs: GameState):
        coords = get_board_coords(
            board_width=gs.board.width, board_height=gs.board.height
        )

        board_state = BoardState.from_game_state(gs=gs, coords=coords)

        return cls(
            board_height=gs.board.height,
            board_width=gs.board.width,
            coords=coords,
            frames=[board_state],
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
