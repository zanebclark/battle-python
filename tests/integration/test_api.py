import dataclasses
import pytest
import os
import requests
import boto3

from battle_python.BattlesnakeTypes import (
    BattlesnakeDetails,
    Coordinate,
    GameStarted,
    GameState,
)
from ..mocks.MockBattlesnakeTypes import (
    get_mock_battlesnake,
    get_mock_standard_board,
    get_mock_standard_game,
)


@pytest.fixture(scope="session")
def battlesnake_url() -> str:
    if os.environ.get("BATTLESNAKEAPIURL") is None:
        stack_name = "battle-python-dev"
        cf_client = boto3.client("cloudformation", region_name="us-west-2")
        response = cf_client.describe_stacks(StackName=stack_name)
        outputs = response["Stacks"][0]["Outputs"]
        for output in outputs:
            if output["OutputKey"] == "BattlesnakeApiUrl":
                return f"{output['OutputValue']}Prod"
        raise Exception(
            f"{stack_name} cloudformation deployment BattlesnakeApiUrl not found"
        )
    else:
        return f"{os.environ['BATTLESNAKEAPIURL']}Prod"


def test_populated_battlesnake_details(battlesnake_url: str):
    response = requests.get(battlesnake_url)
    BattlesnakeDetails(**response.json())
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
    response = requests.post(f"{battlesnake_url}/start", data=dataclasses.asdict(data))
    assert response.status_code == 200


def test_populated_move(battlesnake_url: str):
    data = GameState(
        game=get_mock_standard_game(),
        turn=12,
        board=get_mock_standard_board(food_coords=[(1, 1), (10, 10)]),
        you=get_mock_battlesnake(
            body=[Coordinate(x=0, y=0), Coordinate(x=0, y=1), Coordinate(x=0, y=2)]
        ),
    )
    response = requests.post(f"{battlesnake_url}/move", data=dataclasses.asdict(data))
    assert response.status_code == 200


def test_populated_game_over(battlesnake_url: str):
    data = GameState(
        game=get_mock_standard_game(),
        turn=12,
        board=get_mock_standard_board(food_coords=[(1, 1), (10, 10)]),
        you=get_mock_battlesnake(
            body=[Coordinate(x=0, y=0), Coordinate(x=0, y=1), Coordinate(x=0, y=2)]
        ),
    )
    response = requests.post(f"{battlesnake_url}/end", data=dataclasses.asdict(data))
    assert response.status_code == 200
