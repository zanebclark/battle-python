import uuid

import pytest

from battle_python.BoardState import BoardState
from battle_python.GameState import GameState
from battle_python.SnakeState import SnakeState
from battle_python.api_types import (
    Coord,
    SnakeRequest,
    Game,
    Ruleset,
    Board,
)
from mocks.get_mock_board_state import get_mock_board_state
from mocks.get_mock_snake_state import get_mock_snake_state

from mocks.mock_api_types import get_mock_snake


def test_game_state_init():
    you = get_mock_snake(
        body_coords=[
            Coord(x=0, y=0),
            Coord(x=0, y=1),
            Coord(x=0, y=2),
        ]
    )
    snakes = [
        you,
        get_mock_snake(
            body_coords=[
                Coord(x=10, y=0),
                Coord(x=10, y=1),
                Coord(x=10, y=2),
            ]
        ),
    ]

    game = Game(
        id=str(uuid.uuid4()),
        ruleset=Ruleset(
            name="standard",
            version=str(uuid.uuid4()),
            settings={
                "foodSpawnChance": 10,
                "minimumFood": 11,
                "hazardDamagePerTurn": 12,
            },
        ),
        map=str(uuid.uuid4()),
        timeout=123,
        source="league",
    )

    board = Board(
        height=11,
        width=12,
        food=[Coord(x=1, y=1), Coord(x=10, y=10)],
        hazards=[Coord(x=10, y=1), Coord(x=2, y=10)],
        snakes=snakes,
    )

    gs = SnakeRequest(
        game=game,
        turn=12,
        board=board,
        you=you,
    )

    e_gs = GameState.from_payload(payload=gs.model_dump())

    # GameState-level assertions
    assert e_gs.current_turn == gs.turn
    assert len(e_gs.turns.keys()) == 1

    # Board-level assertions
    assert e_gs.board_height == board.height
    assert e_gs.board_width == board.width
    assert list(e_gs.turns[0][0].food_prob.keys()) == board.food
    assert list(e_gs.turns[0][0].hazard_prob.keys()) == board.hazards
    assert e_gs.turns[0][0].turn == gs.turn
    assert len(e_gs.snake_defs.keys()) == len(snakes)
    gs_snakes = [*e_gs.turns[0][0].snake_states]
    for snake in snakes:
        assert e_gs.snake_defs[snake.id].name == snake.name
        assert e_gs.snake_defs[snake.id].customizations == snake.customizations
        assert e_gs.snake_defs[snake.id].is_self == (snake.id == you.id)

        gs_snake: SnakeState | None = None
        for index, some_snake in enumerate(gs_snakes):
            if some_snake.snake_id == snake.id:
                gs_snake = gs_snakes.pop(index)
                break

        if not gs_snake:
            raise Exception(f"snake not found: {snake.id}")

        assert gs_snake.state_prob == 1
        assert gs_snake.death_prob == 0
        assert gs_snake.food_prob == 0
        assert gs_snake.murder_prob == 0
        assert gs_snake.health == snake.health
        assert gs_snake.body == snake.body
        assert gs_snake.latency == int(snake.latency)
        assert gs_snake.head == snake.head
        assert gs_snake.length == snake.length
        assert gs_snake.shout == snake.shout
        assert gs_snake.is_self == (snake.id == you.id)

    # Game-level assertions
    assert e_gs.game == gs.game
