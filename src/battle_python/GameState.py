from __future__ import annotations

from collections import deque, defaultdict
from itertools import product

from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import NonNegativeInt, Field

from battle_python.BoardState import BoardState
from battle_python.SnakeState import SnakeState
from battle_python.api_types import (
    Coord,
    Game,
    SnakeDef,
)

DEATH = Coord(x=1000, y=1000)


class GameState(BaseModel):
    game: Game
    board_height: NonNegativeInt
    board_width: NonNegativeInt
    current_board: BoardState
    best_my_snake_board: dict[tuple[int, tuple[Coord]], tuple[BoardState, int]] = Field(
        default_factory=dict
    )
    terminal_counter: int = 0
    counter: int = 0
    explored_states: dict[tuple, dict[tuple, BoardState]] = Field(default_factory=dict)
    frontier: deque[BoardState] = Field(default_factory=deque)
    snake_defs: dict[str, SnakeDef]
    my_snake_id: str

    # noinspection PyNestedDecorators
    @classmethod
    def from_payload(cls, payload: dict) -> GameState:
        game = Game(**payload["game"])

        my_snake_id = payload["you"]["id"]

        snake_defs = {
            snake["id"]: SnakeDef(
                id=snake["id"],
                name=snake["name"],
                customizations=snake["customizations"],
                is_self=snake["id"] == my_snake_id,
            )
            for snake in payload["board"]["snakes"]
        }

        other_snakes: tuple[SnakeState, ...] = tuple(
            (
                SnakeState(
                    id=snake["id"],
                    health=snake["health"],
                    body=snake["body"],
                    head=snake["head"],
                    length=snake["length"],
                    latency=snake["latency"],
                    shout=snake["shout"],
                    is_self=snake["id"] == my_snake_id,
                )
                for snake in payload["board"]["snakes"]
                if snake["id"] != my_snake_id
            )
        )

        board = BoardState.factory(
            turn=payload["turn"],
            board_width=payload["board"]["width"],
            board_height=payload["board"]["height"],
            food_coords=payload["board"]["food"],
            hazard_coords=payload["board"]["hazards"],
            other_snakes=other_snakes,
            my_snake=SnakeState(
                id=payload["you"]["id"],
                health=payload["you"]["health"],
                body=payload["you"]["body"],
                head=payload["you"]["head"],
                length=payload["you"]["length"],
                latency=payload["you"]["latency"],
                shout=payload["you"]["shout"],
                is_self=True,
            ),
            hazard_damage_rate=game.ruleset.settings.hazardDamagePerTurn,
        )
        return GameState(
            game=game,
            board_width=payload["board"]["width"],
            board_height=payload["board"]["height"],
            current_board=board,
            snake_defs=snake_defs,
            my_snake_id=my_snake_id,
        )

    def model_post_init(self, __context) -> None:
        self.frontier.append(self.current_board)
        self.best_my_snake_board[self.current_board.get_my_key()] = (
            self.current_board,
            len(
                self.current_board.get_flood_fill_coords(
                    self.current_board.my_snake.head, max_depth=3
                )
            ),
        )

    def handle(self, board: BoardState) -> BoardState | None:
        self.counter += 1
        if board.is_terminal:
            self.terminal_counter += 1

        my_key = board.get_my_key()
        other_key = board.get_other_key()
        if my_key not in self.best_my_snake_board:
            self.best_my_snake_board[my_key] = (
                board,
                len(board.get_flood_fill_coords(board.my_snake.head, max_depth=3)),
            )

        if my_key in self.explored_states:
            best_my_snake_board, best_flood_fill_coords = self.best_my_snake_board[
                my_key
            ]
            best_my_snake = best_my_snake_board.my_snake
            if (
                board.my_snake.length <= best_my_snake.length
                and board.my_snake.murder_count <= best_my_snake.murder_count
                and board.my_snake.health <= best_my_snake.health
                and any(
                    [
                        board.my_snake.length < best_my_snake.length,
                        board.my_snake.murder_count < best_my_snake.murder_count,
                        board.my_snake.health < best_my_snake.health,
                    ]
                )
            ):
                board.is_terminal = True
                board.terminal_reason = "better-snake-state-available"
            elif (
                board.my_snake.length >= best_my_snake.length
                and board.my_snake.murder_count >= best_my_snake.murder_count
                and board.my_snake.health >= best_my_snake.health
                and any(
                    [
                        board.my_snake.length > best_my_snake.length,
                        board.my_snake.murder_count > best_my_snake.murder_count,
                        board.my_snake.health > best_my_snake.health,
                    ]
                )
                # and len(board.get_flood_fill_coords(board.my_snake.head, max_depth=3))
                # >= best_flood_fill_coords
            ):
                self.best_my_snake_board[my_key] = board, len(
                    board.get_flood_fill_coords(board.my_snake.head, max_depth=3)
                )
                for t_board in self.explored_states[my_key].values():
                    t_board.is_terminal = True
                    t_board.terminal_reason = "better-snake-state-available"

            if other_key in self.explored_states[my_key]:
                # TODO: I'm not really accounting for the count of duplicate states explored here
                explored_board = self.explored_states[my_key][other_key]
                board.next_boards = explored_board.next_boards
                board.terminal_reason = "duplicate"
                return None
            else:
                self.explored_states[my_key][other_key] = board
                return board
        else:
            self.explored_states[my_key] = {other_key: board}
            return board

    def increment_frontier(self):
        next_boards: list[BoardState] = []
        for board in self.frontier:
            if board is None:
                continue
            board.populate_next_boards()
            next_boards.extend(
                [self.handle(next_board) for next_board in board.next_boards]
            )
        self.frontier.clear()
        self.frontier.extend(next_boards)
