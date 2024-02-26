import json
import os
from unittest import mock

import pytest

from battle_python import api
from battle_python.GameState import GameState
from battle_python.api_types import Coord, SnakeDef, SnakeCustomizations
from ..mocks.get_mock_game_state import get_mock_game_state
from ..mocks.get_mock_snake_state import get_mock_snake_state
from ..mocks.MockLambdaContext import MockLambdaContext
from ..mocks.api_gateway_event import get_mock_api_gateway_event
from aws_lambda_powertools.utilities.typing import LambdaContext


@pytest.fixture()
def lambda_context() -> LambdaContext:
    return MockLambdaContext()  # type: ignore


@pytest.fixture
def game_state() -> GameState:
    return get_mock_game_state(
        board_height=11,
        board_width=11,
        food_coords=(
            Coord(x=0, y=2),
            Coord(x=2, y=10),
            Coord(x=8, y=0),
            Coord(x=5, y=5),
            Coord(x=10, y=8),
        ),
        snakes={
            SnakeDef(
                id="A",
                name="A",
                customizations=SnakeCustomizations(head="all-seeing"),
            ): get_mock_snake_state(
                snake_id="A",
                body_coords=(Coord(x=1, y=1), Coord(x=1, y=1), Coord(x=1, y=1)),
                health=100,
            ),
            SnakeDef(
                id="B",
                name="B",
                customizations=SnakeCustomizations(
                    head="caffeine", tail="coffee", color="#9ffcc9"
                ),
            ): get_mock_snake_state(
                snake_id="B",
                is_self=True,
                body_coords=(Coord(x=9, y=1), Coord(x=9, y=1), Coord(x=9, y=1)),
                health=100,
            ),
            SnakeDef(
                id="C",
                name="C",
                customizations=SnakeCustomizations(
                    head="beluga", tail="do-sammy", color="#ab8b9c"
                ),
            ): get_mock_snake_state(
                snake_id="C",
                body_coords=(Coord(x=9, y=9), Coord(x=9, y=9), Coord(x=9, y=9)),
                health=100,
            ),
            SnakeDef(
                id="D",
                name="D",
                customizations=SnakeCustomizations(
                    head="bendr", tail="curled", color="#714bb5"
                ),
            ): get_mock_snake_state(
                snake_id="D",
                body_coords=(Coord(x=1, y=9), Coord(x=1, y=9), Coord(x=1, y=9)),
                health=100,
            ),
        },
    )


def test_populated_battlesnake_details(lambda_context):
    env_vars = {
        "BATTLESNAKE_AUTHOR": "testauthor",
        "BATTLESNAKE_COLOR": "#888888",
        "BATTLESNAKE_HEAD": "all-seeing",
        "BATTLESNAKE_TAIL": "curled",
        "BATTLESNAKE_VERSION": "testversion",
    }
    with mock.patch.dict(os.environ, env_vars, clear=True):
        apigw_event = get_mock_api_gateway_event(method="GET", path="/")
        response = api.lambda_handler(event=apigw_event, context=lambda_context)  # type: ignore
        data = json.loads(response["body"])

        assert response["statusCode"] == 200
        assert data["apiversion"] == "1"
        assert (
            data["author"] == env_vars["BATTLESNAKE_AUTHOR"]
        )  # TODO: Do I need to assert that none of the values are null?
        assert data["color"] == env_vars["BATTLESNAKE_COLOR"]
        assert data["head"] == env_vars["BATTLESNAKE_HEAD"]
        assert data["tail"] == env_vars["BATTLESNAKE_TAIL"]
        assert data["version"] == env_vars["BATTLESNAKE_VERSION"]


def test_game_started(lambda_context, game_state: GameState):
    body = game_state.current_board.get_move_request(
        snake_defs=game_state.snake_defs, game=game_state.game
    )
    apigw_event = get_mock_api_gateway_event(method="POST", path="/start", body=body)
    response = api.lambda_handler(event=apigw_event, context=lambda_context)  # type: ignore
    assert response["statusCode"] == 200


def test_move(lambda_context, game_state: GameState):
    body = game_state.current_board.get_move_request(
        snake_defs=game_state.snake_defs, game=game_state.game
    )
    apigw_event = get_mock_api_gateway_event(method="POST", path="/move", body=body)
    response = api.lambda_handler(event=apigw_event, context=lambda_context)  # type: ignore
    assert response["statusCode"] == 200


def test_end(lambda_context, game_state: GameState):
    body = game_state.current_board.get_move_request(
        snake_defs=game_state.snake_defs, game=game_state.game
    )
    apigw_event = get_mock_api_gateway_event(method="POST", path="/end", body=body)
    response = api.lambda_handler(event=apigw_event, context=lambda_context)  # type: ignore
    assert response["statusCode"] == 200
