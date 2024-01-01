import json
import os
import pytest

import requests

from battle_python.BattlesnakeTypes import (
    BattlesnakeDetails,
    Coordinate,
    GameStarted,
    GameState,
)
from tests.mocks.MockBattlesnakeTypes import (
    get_mock_battlesnake,
    get_mock_standard_board,
    get_mock_standard_game,
)


@pytest.fixture
def battlesnake_url() -> str:
    url = os.environ.get("BATTLESNAKEAPIURL")
    return f"{url}Prod"


def test_populated_battlesnake_details(battlesnake_url: str):
    response = requests.get(battlesnake_url)
    payload = json.loads(response.json())
    BattlesnakeDetails(**payload)
    assert response.status_code == 200


def test_populated_game_started(battlesnake_url: str):
    data = GameStarted(
        game=get_mock_standard_game(),
        turn=0,
        board=get_mock_standard_board(food_coords=[(1, 1), (10, 10)]),
        you=get_mock_battlesnake(
            body=[Coordinate(x=0, y=0), Coordinate(x=0, y=1), Coordinate(x=0, y=2)]
        ),
    )
    response = requests.post(f"{battlesnake_url}/start", data=data)


def test_populated_move(battlesnake_url: str):
    data = GameState(
        game=get_mock_standard_game(),
        turn=12,
        board=get_mock_standard_board(food_coords=[(1, 1), (10, 10)]),
        you=get_mock_battlesnake(
            body=[Coordinate(x=0, y=0), Coordinate(x=0, y=1), Coordinate(x=0, y=2)]
        ),
    )
    response = requests.post(f"{battlesnake_url}/move", data=data)


def test_populated_game_over(battlesnake_url: str):
    data = GameState(
        game=get_mock_standard_game(),
        turn=12,
        board=get_mock_standard_board(food_coords=[(1, 1), (10, 10)]),
        you=get_mock_battlesnake(
            body=[Coordinate(x=0, y=0), Coordinate(x=0, y=1), Coordinate(x=0, y=2)]
        ),
    )
    response = requests.post(f"{battlesnake_url}/end", data=data)
