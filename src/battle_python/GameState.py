from __future__ import annotations

from collections import deque, defaultdict

from aws_lambda_powertools.utilities.parser import BaseModel
from pydantic import NonNegativeInt, Field
from aws_lambda_powertools import Logger

from battle_python.BoardState import BoardState
from battle_python.SnakeState import SnakeState
from battle_python.api_types import (
    Coord,
    Game,
    SnakeDef,
)

logger = Logger()


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

    def get_next_move(self):
        for turn in range(2):
            self.increment_frontier()

        head_scores = defaultdict(list)
        [
            head_scores[board.my_snake.head].append(board.score)
            for board in self.current_board.next_boards
        ]
        logger.info("available scores", head_scores=str(head_scores))

        best_coord = sorted(
            {
                head: (sum(numbers) / len(numbers))
                for head, numbers in head_scores.items()
            }.items(),
            key=lambda item: item[1],
            reverse=True,
        )[0][0]

        direction = Coord(
            x=self.current_board.my_snake.head.x - best_coord.x,
            y=self.current_board.my_snake.head.y - best_coord.y,
        )

        if self.current_board.my_snake.head + Coord(x=-1, y=0) == best_coord:
            logger.info("returning left")
            return "left"
        elif self.current_board.my_snake.head + Coord(x=1, y=0) == best_coord:
            logger.info("returning right")
            return "right"
        elif self.current_board.my_snake.head + Coord(x=0, y=-1) == best_coord:
            logger.info("returning down")
            return "down"
        elif self.current_board.my_snake.head + Coord(x=0, y=1) == best_coord:
            logger.info("returning up")
            return "up"
        else:
            raise Exception(f"Unhandled direction: {direction}")
