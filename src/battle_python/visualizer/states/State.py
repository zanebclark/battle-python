from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque
from typing import Protocol

import pygame
from battle_python.visualizer.Actions import Actions


class GameProtocol(Protocol):
    state_stack: deque[State]
    game_width: int
    game_height: int

    def reset_keys(self):
        ...

    def draw_text(
        self, surface: pygame.Surface, text: str, color: pygame.Color, x: int, y: int
    ):
        ...


class State(ABC):
    game: GameProtocol
    prev_state: State | None

    def __init__(self, game: GameProtocol):
        self.game = game
        self.prev_state = None

    @abstractmethod
    def update(self, delta_time: float, actions: Actions):
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface):
        pass

    def enter_state(self):
        if len(self.game.state_stack) > 1:
            self.prev_state = self.game.state_stack[-1]
        self.game.state_stack.append(self)

    def exit_state(self):
        self.game.state_stack.pop()
