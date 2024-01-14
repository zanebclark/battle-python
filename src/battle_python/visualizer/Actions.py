from __future__ import annotations

import pygame
from dataclasses import dataclass, fields

EVENT_MAPPING: dict[int, str] = {
    pygame.K_a: "left",
    pygame.K_d: "right",
    pygame.K_w: "up",
    pygame.K_s: "down",
    pygame.K_p: "action1",
    pygame.K_o: "action2",
    pygame.K_RETURN: "enter",
    pygame.K_ESCAPE: "exit",
}


@dataclass
class Actions:
    left: bool = False
    right: bool = False
    up: bool = False
    down: bool = False
    action1: bool = False
    action2: bool = False
    enter: bool = False
    exit: bool = False

    def process_event(self, event: pygame):
        if event.type == pygame.QUIT:
            self.exit = True
        elif hasattr(event, "key") and event.key in EVENT_MAPPING.keys():
            setattr(self, EVENT_MAPPING[event.key], event.type == pygame.KEYDOWN)

    def reset(self):
        for field in fields(self):
            setattr(self, field.name, False)
