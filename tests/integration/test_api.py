from pathlib import Path

import pytest
import os
import requests
import boto3
from dotenv import load_dotenv

from battle_python.GameState import GameState
from battle_python.api_types import (
    Coord,
    SnakeMetadataResponse,
    SnakeDef,
    SnakeCustomizations,
)
from ..mocks.get_mock_game_state import get_mock_game_state
from ..mocks.get_mock_snake_state import get_mock_snake_state

load_dotenv(Path(__file__).parent.parent.parent / ".env")


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


def test_populated_battlesnake_details(battlesnake_url: str) -> None:
    response = requests.get(battlesnake_url)
    SnakeMetadataResponse(**response.json())
    assert response.status_code == 200


@pytest.mark.parametrize(
    "turn, path",
    [
        (0, "start"),
        (12, "move"),
        (24, "end"),
    ],
)
def test_populated_api_endpoints(
    battlesnake_url: str, game_state: GameState, turn: int, path: str
) -> None:
    data = game_state.current_board.get_move_request(
        snake_defs=game_state.snake_defs, game=game_state.game
    )

    response = requests.post(f"{battlesnake_url}/{path}", json=data)
    assert response.status_code == 200
