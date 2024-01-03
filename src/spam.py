from __future__ import annotations
from ast import List
from dataclasses import dataclass
from typing import Dict, Literal, Tuple, Optional
import pygame


@dataclass
class Cell:
    start: int
    end: int
    fill_start: int
    fill_end: int
    contents: Optional[Literal["vertical_snake", "horizontal_snake", "food", "fog"]]


@dataclass
class Game:
    board_height: int
    board_width: int
    cells: List[Cell]

    # @classmethod
    # def factory(cls, board_height: int, board_width: int) -> Game:
    #     return cls(board_height=board_height,board_width=board_width, cells=cells)


colors: Dict[str, Tuple[int, int, int]] = {
    "white": (255, 255, 255),
    "blue": (0, 0, 255),
    "red": (255, 0, 0),
}


class BattlesnakeGame:
    def __init__(self, caption: str, width: int, height: int, fps: int):
        self.width: int = width
        self.height: int = height
        self.fps: int = fps
        self.display = pygame.display.set_caption(caption)
        self.window = pygame.display.set_mode((width, height))
        self.clock: pygame.time.Clock = pygame.time.Clock()

    def draw_window(self) -> None:
        self.window.fill(color=colors["white"])
        pygame.display.update()

    def main_loop(self) -> None:
        self.clock.tick(self.fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            self.draw_window()
            pygame.draw.rect(self.window, colors["blue"], [200, 150, 10, 10])
            for coord in range(0, self.width, 50):
                pygame.draw.line(
                    self.window,
                    colors["blue"],
                    start_pos=(1, coord),
                    end_pos=(self.height, coord),
                    width=4,
                )
                pygame.draw.line(
                    self.window,
                    colors["blue"],
                    start_pos=(coord, 1),
                    end_pos=(coord, self.width),
                    width=4,
                )
            pygame.display.update()
        return True


def main():
    board = Game.factory(board_height=11, board_width=11)
    spam = BattlesnakeGame(width=500, height=500, fps=60, caption="Venisssss Beach")
    run = True
    while run:
        run = spam.main_loop()


if __name__ == "__main__":
    main()
