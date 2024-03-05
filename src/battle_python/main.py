import time
from typing import Literal
from fastapi import FastAPI, HTTPException
import structlog

from battle_python.GameState import GameState
from battle_python.api_types import SnakeMetadataResponse, SnakeRequest

RestMethod = Literal["GET", "POST"]
api = FastAPI()
logger = structlog.get_logger()
# TODO: Anticipate hazard progression


@api.get("/")
def battlesnake_details() -> dict:
    return SnakeMetadataResponse(
        author="zanebclark",
        color="#ab8b9c",
        head="beluga",
        tail="do-sammy",
        version="terraform-v1",
    ).model_dump()


@api.post("/start")
def game_started(move_request: SnakeRequest) -> dict[str, int | str]:
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        game_id=move_request.game.id,
        my_snake_id=move_request.you.id,
        turn=move_request.turn,
    )
    # try:
    #     parse(event=body, model=SnakeRequest)
    # except Exception:
    #     return {"status_code": 400, "message": "Invalid order"}
    return {"message": "Let's get to it!"}


@api.post("/move")
def move(move_request: SnakeRequest) -> dict[str, int | str]:
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        game_id=move_request.game.id,
        my_snake_id=move_request.you.id,
        turn=move_request.turn,
    )

    request_time = time.time_ns() // 1_000_000
    try:
        gs = GameState.from_snake_request(move_request=move_request)
        direction = gs.get_next_move(request_time)
        ms_elapsed = (time.time_ns() // 1_000_000) - request_time
        logger.debug(
            "returning move",
            ms_elapsed=ms_elapsed,
            move=direction,
        )
        return {"move": direction}
    except Exception:
        raise HTTPException(status_code=404)


@api.post("/end")
def game_over(move_request: SnakeRequest) -> dict[str, int | str]:
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        game_id=move_request.game.id,
        my_snake_id=move_request.you.id,
        turn=move_request.turn,
    )

    # try:
    #     parse(event=body, model=SnakeRequest)
    # except ValidationError:
    #     return {"status_code": 400, "message": "Invalid order"}

    return {"message": "Good game!"}


# TODO: If the battlesnake is going to run out of health and die, take this into account with probabilities
# TODO: If the battlesnake consistently times out, take this into account with probabilities
