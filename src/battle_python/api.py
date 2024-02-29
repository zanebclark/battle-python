import os
import time
from typing import Literal
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.parser import parse, ValidationError
from aws_lambda_powertools import Logger
from aws_lambda_powertools import Metrics

logger = Logger()

from battle_python.GameState import GameState
from battle_python.api_types import SnakeMetadataResponse, SnakeRequest

RestMethod = Literal["GET", "POST"]
api = APIGatewayRestResolver()
metrics = Metrics(namespace="Powertools")

# TODO: Anticipate hazard progression


@api.get("/")
def battlesnake_details() -> dict:
    return SnakeMetadataResponse(
        author=os.environ.get("BATTLESNAKE_AUTHOR"),
        color=os.environ.get("BATTLESNAKE_COLOR"),
        head=os.environ.get("BATTLESNAKE_HEAD"),
        tail=os.environ.get("BATTLESNAKE_TAIL"),
        version=os.environ.get("BATTLESNAKE_VERSION"),
    ).model_dump()


@api.post("/start")
def game_started() -> dict[str, int | str]:
    body = api.current_event.json_body
    logger.append_keys(game_id=body["game"]["id"])
    logger.append_keys(turn=body["turn"])
    try:
        parse(event=body, model=SnakeRequest)
    except ValidationError:
        return {"status_code": 400, "message": "Invalid order"}
    return {"status_code": 200, "message": "Let's get to it!"}


@api.post("/move")
def move() -> dict[str, int | str]:
    body = api.current_event.json_body

    logger.append_keys(game_id=body["game"]["id"])
    logger.append_keys(my_snake_id=body["you"]["id"])
    logger.append_keys(turn=body["turn"])

    request_time = api.current_event.request_context.request_time_epoch
    try:
        gs = GameState.from_payload(api.current_event.json_body)
        move = gs.get_next_move(request_time)
        ms_elapsed = (time.time_ns() // 1_000_000) - request_time
        logger.debug(
            "returning move",
            ms_elapsed=ms_elapsed,
            move=move,
        )
        return {"move": move}
    except ValidationError:
        return {"status_code": 400, "message": "Invalid"}


@api.post("/end")
def game_over() -> dict[str, int | str]:
    body = api.current_event.json_body

    logger.append_keys(game_id=body["game"]["id"])
    logger.append_keys(turn=body["turn"])

    try:
        parse(event=body, model=SnakeRequest)
    except ValidationError:
        return {"status_code": 400, "message": "Invalid order"}

    return {"status_code": 200, "message": "Good game!"}


# Enrich logging with contextual information from Lambda
@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_REST,
    log_event=True,
    clear_state=True,
)
# ensures metrics are flushed upon request completion/failure and capturing ColdStart metric
@metrics.log_metrics(capture_cold_start_metric=True)  # type: ignore
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return api.resolve(event, context)


# TODO: If the battlesnake is going to run out of health and die, take this into account with probabilities
# TODO: If the battlesnake consistently times out, take this into account with probabilities
