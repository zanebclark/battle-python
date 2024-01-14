from __future__ import annotations
from pathlib import Path

import pygame
from collections import deque
import time

from battle_python.visualizer.Actions import Actions
from battle_python.visualizer.states.State import State
from battle_python.visualizer.states.Title import Title


class Game:
    game_width: int
    game_height: int
    screen_width: int
    screen_height: int
    game_canvas: pygame.Surface
    screen: pygame.Surface
    running: bool
    playing: bool
    actions: Actions
    dt: float
    prev_time: float
    state_stack: deque[State]
    title_screen: Title | None

    def __init__(self):
        pygame.init()
        self.game_width = 480
        self.game_height = 480
        self.screen_width = 960
        self.screen_height = 960
        self.game_canvas = pygame.Surface((self.game_width, self.game_height))
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), flags=pygame.RESIZABLE
        )
        self.running = True
        self.playing = True
        self.actions = Actions()
        self.dt = 0
        self.prev_time = 0
        self.state_stack = deque()
        self.assets_dir = Path(__file__).parent / "assets"
        self.font_dir = self.assets_dir / "font"
        font_file = self.font_dir / "PressStart2P-vaV7.ttf"
        self.font = pygame.font.Font(str(font_file), 20)
        self.title_screen = None

        self.load_states()

    def game_loop(self):
        while self.playing:
            self.get_dt()
            self.get_events()
            self.update()
            self.render()

    def get_events(self):
        for event in pygame.event.get():
            self.actions.process_event(event)

            if self.actions.exit:
                self.playing = False
                self.running = False

    def update(self):
        self.state_stack[-1].update(self.dt, self.actions)

    def render(self):
        self.state_stack[-1].render(self.game_canvas)
        self.screen.blit(
            pygame.transform.scale(
                self.game_canvas, (self.screen_width, self.screen_height)
            ),
            (0, 0),
        )
        pygame.display.flip()

    def get_dt(self):
        now = time.time()
        self.dt = now - self.prev_time
        self.prev_time = now

    def draw_text(
        self, surface: pygame.Surface, text: str, color: pygame.Color, x: int, y: int
    ):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)

    def load_states(self):
        self.title_screen = Title(self)
        self.state_stack.append(self.title_screen)

    def reset_keys(self):
        self.actions.reset()


if __name__ == "__main__":
    g = Game()
    while g.running:
        g.game_loop()
