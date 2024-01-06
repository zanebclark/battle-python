import dataclasses
import os
import random
from typing import Literal
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Tracer
from aws_lambda_powertools import Metrics
from dacite import from_dict

from battle_python.api_types import BattlesnakeDetails, MoveResponse, GameState
from battle_python.pathfinder import resolve_collisions

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
    body = api.current_event.json_body
    logger.append_keys(game_id=body["game"]["id"])
    logger.append_keys(turn=body["turn"])
    gs = from_dict(data_class=GameState, data=body)
    return None


@api.post("/move")
@tracer.capture_method
def move() -> dict:
    body = api.current_event.json_body
    logger.append_keys(game_id=body["game"]["id"])
    logger.append_keys(turn=body["turn"])
    gs = from_dict(data_class=GameState, data=body)
    resolve_collisions(gs=gs, turn=gs.turn)
    turn_prob = gs.board.snake_dict[gs.you.id].turn_prob[gs.turn]
    available_moves = [
        spam.direction for spam in turn_prob.values() if spam.body_index == 0
    ]

    return dataclasses.asdict(MoveResponse(move=random.choice(available_moves)))


@api.post("/end")
@tracer.capture_method
def game_over() -> None:
    body = api.current_event.json_body
    logger.append_keys(game_id=body["game"]["id"])
    logger.append_keys(turn=body["turn"])
    gs = from_dict(data_class=GameState, data=body)
    return None


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
