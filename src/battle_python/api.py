import dataclasses
import os
from typing import Literal
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Metrics
from aws_lambda_powertools.metrics import MetricUnit

from battle_python.BattlesnakeTypes import (
    BattlesnakeDetails,
    GameStarted,
    GameState,
    MoveResponse,
)

RestMethod = Literal["GET", "POST"]
api = APIGatewayRestResolver()
tracer = Tracer()
logger = Logger()
metrics = Metrics(namespace="Powertools")


@api.get("/")
@tracer.capture_method
def battlesnake_details() -> BattlesnakeDetails:
    return BattlesnakeDetails(
        author=os.environ.get("BATTLESNAKE_AUTHOR"),
        color=os.environ.get("BATTLESNAKE_COLOR"),
        head=os.environ.get("BATTLESNAKE_HEAD"),
        tail=os.environ.get("BATTLESNAKE_TAIL"),
        version=os.environ.get("BATTLESNAKE_VERSION"),
    )  # TODO: Do I need to filter out None?


@api.post("/start")
@tracer.capture_method
def game_started() -> None:
    game_started = GameStarted(**api.current_event.json_body)
    return None


@api.post("/move")
@tracer.capture_method
def move() -> MoveResponse:
    return MoveResponse(move="up")


@api.post("/end")
@tracer.capture_method
def game_over(game_state: GameState) -> None:
    return None


# Enrich logging with contextual information from Lambda
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
# Adding tracer
# See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/tracer/
@tracer.capture_lambda_handler
# ensures metrics are flushed upon request completion/failure and capturing ColdStart metric
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    logger.info("event", extra=event)
    return api.resolve(event, context)
