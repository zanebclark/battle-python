from __future__ import annotations
import pygame
from battle_python.visualizer.states.State import State, GameProtocol
from battle_python.visualizer.Actions import Actions


class Title(State):
    def __init__(self, game: GameProtocol):
        super().__init__(game=game)

    def update(self, delta_time: float, actions: Actions):
        self.game.reset_keys()

    def render(self, display: pygame.Surface):
        display.fill((255, 255, 255))
        self.game.draw_text(
            display,
            "Game States Demo",
            pygame.Color(0, 0, 0),
            self.game.game_width // 2,
            self.game.game_height // 2,
        )
