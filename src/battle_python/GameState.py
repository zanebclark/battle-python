from __future__ import annotations

import time
from collections import deque
from itertools import groupby

from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import NonNegativeInt, Field
from aws_lambda_powertools import Logger
from aws_lambda_powertools.tracing import Tracer

from battle_python.BoardState import BoardState
from battle_python.SnakeState import SnakeState
from battle_python.api_types import (
    Coord,
    Game,
    SnakeDef,
)

logger = Logger()
tracer = Tracer()


class TimeoutException(Exception):
    pass


class GameState(BaseModel):
    game: Game
    board_height: NonNegativeInt
    board_width: NonNegativeInt
    current_board: BoardState
    best_my_snake_board: dict[tuple[int, tuple[Coord]], BoardState] = Field(
        default_factory=dict
    )
    terminal_counter: int = 0
    counter: int = 0
    explored_states: dict[tuple, dict[tuple, BoardState]] = Field(default_factory=dict)
    frontier: deque[BoardState] = Field(default_factory=deque)
    snake_defs: dict[str, SnakeDef]

    # noinspection PyNestedDecorators
    @classmethod
    def from_payload(cls, payload: dict) -> GameState:
        game = Game(**payload["game"])

        snake_defs = {
            snake["id"]: SnakeDef(
                id=snake["id"],
                name=snake["name"],
                customizations=snake["customizations"],
                is_self=snake["id"] == payload["you"]["id"],
            )
            for snake in payload["board"]["snakes"]
        }

        other_snakes: tuple[SnakeState, ...] = tuple(
            (
                SnakeState(
                    id=snake["id"],
                    health=snake["health"],
                    body=tuple(
                        Coord(x=coord["x"], y=coord["y"]) for coord in snake["body"]
                    ),
                    head=snake["head"],
                    length=snake["length"],
                    latency=snake["latency"],
                    shout=snake["shout"],
                    is_self=snake["id"] == payload["you"]["id"],
                )
                for snake in payload["board"]["snakes"]
                if snake["id"] != payload["you"]["id"]
            )
        )

        board = BoardState.factory(
            turn=payload["turn"],
            board_width=payload["board"]["width"],
            board_height=payload["board"]["height"],
            food_coords=tuple(
                Coord(x=coord["x"], y=coord["y"]) for coord in payload["board"]["food"]
            ),
            hazard_coords=payload["board"]["hazards"],
            other_snakes=other_snakes,
            my_snake=SnakeState(
                id=payload["you"]["id"],
                health=payload["you"]["health"],
                body=tuple(
                    Coord(x=coord["x"], y=coord["y"])
                    for coord in payload["you"]["body"]
                ),
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
        )

    def model_post_init(self, __context) -> None:
        self.frontier.append(self.current_board)
        self.best_my_snake_board[self.current_board.get_my_key()] = self.current_board

    @tracer.capture_method
    def handle(self, board: BoardState) -> BoardState | None:
        self.counter += 1
        if board.is_terminal:
            self.terminal_counter += 1

        my_key = board.get_my_key()
        other_key = board.get_other_key()
        if my_key not in self.best_my_snake_board:
            self.best_my_snake_board[my_key] = board

        if my_key in self.explored_states:
            best_my_snake_board = self.best_my_snake_board[my_key]
            if (
                board.my_snake.length <= best_my_snake_board.my_snake.length
                and board.my_snake.murder_count
                <= best_my_snake_board.my_snake.murder_count
                and board.my_snake.health <= best_my_snake_board.my_snake.health
                and board.score <= best_my_snake_board.score
                and any(
                    [
                        board.my_snake.length < best_my_snake_board.my_snake.length,
                        board.my_snake.murder_count
                        < best_my_snake_board.my_snake.murder_count,
                        board.my_snake.health < best_my_snake_board.my_snake.health,
                        board.score < best_my_snake_board.score,
                    ]
                )
            ):
                board.is_terminal = True
                board.terminal_reason = "better-snake-state-available"
            elif (
                board.my_snake.length >= best_my_snake_board.my_snake.length
                and board.my_snake.murder_count
                >= best_my_snake_board.my_snake.murder_count
                and board.my_snake.health >= best_my_snake_board.my_snake.health
                and board.score >= best_my_snake_board.score
                and any(
                    [
                        board.my_snake.length > best_my_snake_board.my_snake.length,
                        board.my_snake.murder_count
                        > best_my_snake_board.my_snake.murder_count,
                        board.my_snake.health > best_my_snake_board.my_snake.health,
                        board.score > best_my_snake_board.score,
                    ]
                )
            ):
                self.best_my_snake_board[my_key] = board
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

    @tracer.capture_method
    def increment_frontier(self, request_time: float):
        next_boards: list[BoardState] = []
        for board in self.frontier:
            if board is None:
                continue
            board.populate_next_boards()
            next_boards.extend(
                [self.handle(next_board) for next_board in board.next_boards]
            )
            if (time.time_ns() // 1_000_000) > (request_time + 320):
                raise TimeoutException()
        self.frontier.clear()
        self.frontier.extend(next_boards)

    @tracer.capture_method
    def get_next_move(self, request_time: float):
        try:
            while len(self.frontier) > 0:
                if (time.time_ns() // 1_000_000) > (request_time + 320):
                    raise TimeoutException()
                logger.debug("incrementing frontier")
                self.increment_frontier(request_time=request_time)
        except TimeoutException:
            pass

        min_score_per_head = {
            head_coord: min([board.score for board in boards])
            for head_coord, boards in groupby(
                self.current_board.next_boards, key=lambda board: board.my_snake.head
            )
        }

        if len(min_score_per_head.keys()) == 0:
            return "up"

        best_head_score = sorted(
            min_score_per_head.items(),
            key=lambda item: item[1],
            reverse=True,
        )[0][0]

        direction = Coord(
            x=self.current_board.my_snake.head.x - best_head_score.x,
            y=self.current_board.my_snake.head.y - best_head_score.y,
        )

        if self.current_board.my_snake.head + Coord(x=-1, y=0) == best_head_score:
            move = "left"
        elif self.current_board.my_snake.head + Coord(x=1, y=0) == best_head_score:
            move = "right"
        elif self.current_board.my_snake.head + Coord(x=0, y=-1) == best_head_score:
            move = "down"
        elif self.current_board.my_snake.head + Coord(x=0, y=1) == best_head_score:
            move = "up"
        else:
            raise Exception(f"Unhandled direction: {direction}")

        logger.info(
            "get_next_move",
            best_head_score=f"({best_head_score.x}, {best_head_score.y})",
            average_head_scores=[
                f"({coord.x},{coord.y}): {score}"
                for coord, score in min_score_per_head.items()
            ],
            move=move,
            boards_explored=self.counter,
            terminal_boards=self.terminal_counter,
        )

        return move
