import random
from dataclasses import dataclass

from battle_python.GameState import GameState


@dataclass
class Game:
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
        # your_snake.body.insert(0, move)

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
