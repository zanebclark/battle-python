from __future__ import annotations

import time
from typing import Type, TypeVar

from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
from boto3.session import Session
from ec2_metadata import ec2_metadata
from requests import ConnectionError
from pydantic import BaseModel

from battle_python.api_types import SnakeRequest

T = TypeVar("T", bound="DynamoDBTable")


def get_region_name() -> str:
    try:
        return ec2_metadata.region
    except ConnectionError:
        return "us-west-2"


def get_dynamodb_table(
    session: Session, table_name: str
) -> DynamoDBServiceResource.Table:
    dynamodb: DynamoDBServiceResource = session.resource("dynamodb")
    table = dynamodb.Table(table_name)
    table.load()
    return table


class GamesTable(BaseModel):
    table: DynamoDBServiceResource.Table

    @classmethod
    def factory(cls, session: Session) -> GamesTable:
        table = get_dynamodb_table(session=session, table_name="battlesnakesGames")
        return cls(table=table)

    def add_game(self, request: SnakeRequest):
        self.table.put_item(
            Item={
                "snakeGameID": request.snake_game_id,
                "gameID": request.game.id,
                "snakeID": request.you.id,
                "game": request.game,
                "expireAt": int(time.time()) + 604800,  # seconds in a week
            }
        )

    def update_game(
        self,
        request: SnakeRequest,
        final_turn: int,
    ):
        self.table.update_item(
            Key={
                "snakeGameID": {
                    "S": request.snake_game_id,
                },
            },
            ExpressionAttributeNames={
                "#FT": "finalTurn",
            },
            ExpressionAttributeValues={
                ":ft": final_turn,
            },
            UpdateExpression="SET #FT = :ft",
            ReturnValues="UPDATED_NEW",
        )


class RequestsTable(BaseModel):
    table: DynamoDBServiceResource.Table

    @classmethod
    def factory(cls, session: Session) -> RequestsTable:
        table = get_dynamodb_table(session=session, table_name="battlesnakesRequests")
        return cls(table=table)

    def add_request(self, request: SnakeRequest):
        self.table.put_item(
            Item={
                "snakeGameID": request.snake_game_id,
                "expireAt": int(time.time()) + 604800,  # seconds in a week
                **request.model_dump(),
            }
        )

    def update_request(
        self,
        request: SnakeRequest,
        move: str,
        shout: str | None,
        latency: int,
        boards_explored: int,
    ):
        self.table.update_item(
            Key={
                "snakeGameID": {
                    "S": request.snake_game_id,
                },
                "turn": {"N": request.turn},
            },
            ExpressionAttributeNames={
                "#M": "move",
                "#S": "shout",
                "#L": "latency",
                "#BE": "boardsExplored",
            },
            ExpressionAttributeValues={
                ":m": move,
                ":s": shout,
                ":l": latency,
                ":be": boards_explored,
            },
            UpdateExpression="SET #M = :m, #S = :s, #L = :l, #BE = :be",
            ReturnValues="UPDATED_NEW",
        )


if __name__ == "__main__":
    region_name = get_region_name()
    session = Session(region_name=region_name)
    games_table = GamesTable.factory(session=session)
    requests_table = RequestsTable.factory(session=session)
    print("hey there!")

# TODO: Create a background task to write to DynamoDB after a response is provided.
# TODO: Include latency of the response for each request.
