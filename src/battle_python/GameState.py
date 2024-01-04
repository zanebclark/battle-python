from dataclasses import dataclass, field
from battle_python.Battlesnake import Battlesnake, get_combined_coord_prob_dict

from battle_python.types import Board, Coord, Game, get_board_coords


@dataclass(frozen=True)
class CoordState(Coord):
    is_food_prob: int
    is_hazard_prob: int
    prob_dict: dict[str, int]


@dataclass
class GameState:
    game: Game
    turn: int
    board: Board
    you: Battlesnake
    cells: dict[Coord, CoordState] | None = field(init=False)

    def enrich_snakes(self):
        for snake in self.board.snakes:
            snake.board_width = self.board.width
            snake.board_height = self.board.height
            snake.turn = self.turn
            if snake.id == self.you.id:
                snake.is_self = True
                continue

    def get_cells(self) -> dict[Coord, CoordState]:
        cells: dict[Coord, CoordState] = {}
        turn = self.turn
        snakes = self.board.snakes

        coord_prob_dict = get_combined_coord_prob_dict(snakes=snakes)

        coords = get_board_coords(
            board_width=self.board.width, board_height=self.board.height
        )

        for coord in coords:
            is_food_prob = 100 if coord in self.board.food else 0
            is_hazard_prob = 100 if coord in self.board.hazards else 0
            prob_dict = coord_prob_dict.get(coord)

            cells[coord] = CoordState(
                x=coord.x,
                y=coord.y,
                is_food_prob=is_food_prob,
                is_hazard_prob=is_hazard_prob,
                prob_dict=prob_dict,
            )

        return cells

    def __post_init__(self):
        self.enrich_snakes()
        self.cells = self.get_cells()
