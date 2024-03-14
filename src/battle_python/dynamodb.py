from __future__ import annotations

import time
from typing import Any

from boto3.session import Session
from ec2_metadata import ec2_metadata
from requests import ConnectionError
from pydantic import BaseModel, ConfigDict

from battle_python.api_types import SnakeRequest


def get_region_name() -> str:
    try:
        return ec2_metadata.region
    except ConnectionError:
        return "us-west-2"


def get_dynamodb_table(table_name: str) -> Any:
    region_name = get_region_name()
    session = Session(region_name=region_name)
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(table_name)
    table.load()
    return table


class GamesTable(BaseModel):
    table: Any

    @classmethod
    def factory(cls) -> GamesTable:
        table = get_dynamodb_table(table_name="battlesnakesGames")
        return cls(table=table)

    def add_game(self, request: SnakeRequest) -> None:
        self.table.put_item(
            Item={
                "snakeGameID": request.snake_game_id,
                "gameID": request.game.id,
                "snakeID": request.you.id,
                "game": request.game.model_dump(),
                "expireAt": int(time.time()) + 604800,  # seconds in a week
            }
        )

    def update_game(
        self,
        request: SnakeRequest,
    ) -> None:
        self.table.update_item(
            Key={
                "snakeGameID": request.snake_game_id,
            },
            ExpressionAttributeNames={
                "#FT": "finalTurn",
            },
            ExpressionAttributeValues={
                ":ft": request.turn,
            },
            UpdateExpression="SET #FT = :ft",
            ReturnValues="UPDATED_NEW",
        )


class RequestsTable(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    table: Any

    @classmethod
    def factory(cls) -> RequestsTable:
        table = get_dynamodb_table(table_name="battlesnakesRequests")
        return cls(table=table)

    def add_request(
        self,
        request: SnakeRequest,
        move: str | None = None,
        latency: int | None = None,
        boards_explored: int | None = None,
        terminal_boards: int | None = None,
        exception: bool | None = False,
    ) -> None:
        self.table.put_item(
            Item={
                "snakeGameID": request.snake_game_id,
                "move": move,
                "latency": latency,
                "boardsExplored": boards_explored,
                "terminalBoards": terminal_boards,
                "expireAt": int(time.time()) + 604800,  # seconds in a week
                "exception": exception,
                **request.model_dump(),
            }
        )
