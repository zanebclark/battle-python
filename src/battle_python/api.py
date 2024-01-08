import os
import random
from typing import Literal
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.parser import parse, ValidationError
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Metrics

from battle_python.api_types import SnakeDetails, MoveResponse, GameState
from battle_python.pathfinder import resolve_collisions

RestMethod = Literal["GET", "POST"]
api = APIGatewayRestResolver()
tracer = Tracer()
logger = Logger()
metrics = Metrics(namespace="Powertools")


@api.get("/")
@tracer.capture_method
def battlesnake_details() -> dict:
    return SnakeDetails(
        author=os.environ.get("BATTLESNAKE_AUTHOR"),
        color=os.environ.get("BATTLESNAKE_COLOR"),
        head=os.environ.get("BATTLESNAKE_HEAD"),
        tail=os.environ.get("BATTLESNAKE_TAIL"),
        version=os.environ.get("BATTLESNAKE_VERSION"),
    ).model_dump()


@api.post("/start")
@tracer.capture_method
def game_started() -> dict[str, int | str]:
    body = api.current_event.json_body
    logger.append_keys(game_id=body["game"]["id"])
    logger.append_keys(turn=body["turn"])
    try:
        gs = parse(event=body, model=GameState)
    except ValidationError:
        return {"status_code": 400, "message": "Invalid order"}
    return {"status_code": 200, "message": "Let's get to it!"}


@api.post("/move")
@tracer.capture_method
def move() -> dict[str, int | str]:
    body = api.current_event.json_body

    logger.append_keys(game_id=body["game"]["id"])
    logger.append_keys(turn=body["turn"])

    try:
        gs = parse(event=body, model=GameState)
    except ValidationError:
        return {"status_code": 400, "message": "Invalid order"}

    resolve_collisions(gs=gs, turn=gs.turn)
    turn_prob = gs.board.snake_dict[gs.you.id].turn_prob[gs.turn]
    available_moves = [
        spam.direction for spam in turn_prob.values() if spam.body_index == 0
    ]

    return MoveResponse(move=random.choice(available_moves)).model_dump()


@api.post("/end")
@tracer.capture_method
def game_over() -> dict[str, int | str]:
    body = api.current_event.json_body

    logger.append_keys(game_id=body["game"]["id"])
    logger.append_keys(turn=body["turn"])

    try:
        gs = parse(event=body, model=GameState)
    except ValidationError:
        return {"status_code": 400, "message": "Invalid order"}

    return {"status_code": 200, "message": "Good game!"}


# Enrich logging with contextual information from Lambda
@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_REST,
    log_event=True,
    clear_state=True,
)
# Adding tracer
# See: https://awslabs.github.io/aws-lambda-powertools-python/latest/core/tracer/
@tracer.capture_lambda_handler
# ensures metrics are flushed upon request completion/failure and capturing ColdStart metric
@metrics.log_metrics(capture_cold_start_metric=True)  # type: ignore
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return api.resolve(event, context)


# TODO: If the battlesnake is going to run out of health and die, take this into account with probabilities
# TODO: If the battlesnake consistently times out, take this into account with probabilities
