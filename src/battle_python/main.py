import os
import time
from typing import Literal

from fastapi import FastAPI, HTTPException, Request, APIRouter, Depends
import structlog

from battle_python.GameState import GameState
from battle_python.api_types import SnakeMetadataResponse, SnakeRequest, MoveResponse
from battle_python.logging_config import get_configured_logger


log = get_configured_logger()

RestMethod = Literal["GET", "POST"]
api = FastAPI(
    title="Battlesnake Webhook Handler",
    description="Webhook endpoints called by Battlesnakes.com to play the game",
    version="1.0",
    docs_url=None if os.environ.get("ENV") == "PROD" else "/docs",
)
api_router = APIRouter()

# TODO: Anticipate hazard progression


@api.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


class JSONDecodeErroras:
    pass


async def log_request_info(request: Request):
    structlog.contextvars.clear_contextvars()
    request_body = ""
    if request.url != request.base_url:
        request_body = await request.json()
        structlog.contextvars.bind_contextvars(
            game_id=request_body["game"]["id"],
            my_snake_id=request_body["you"]["id"],
            turn=request_body["turn"],
        )
    log.info(
        f"{request.method}: {request.url} received",
        method=request.method,
        url=request.url,
        headers=request.headers,
        body=request_body,
        path_params=request.path_params,
        query_params=request.query_params,
        cookies=request.cookies,
    )


@api_router.get("/")
def battlesnake_details() -> SnakeMetadataResponse:
    return SnakeMetadataResponse(
        author="zanebclark",
        color="#ab8b9c",
        head="beluga",
        tail="do-sammy",
        version="terraform-v1",
    )


@api_router.post("/start")
def game_started(_: SnakeRequest) -> None:
    pass


@api_router.post("/move")
def move(move_request: SnakeRequest) -> MoveResponse:
    request_time = time.time_ns() // 1_000_000
    try:
        gs = GameState.from_snake_request(move_request=move_request)
        direction = gs.get_next_move(request_time)
        ms_elapsed = (time.time_ns() // 1_000_000) - request_time
        log.debug(
            "returning move",
            ms_elapsed=ms_elapsed,
            move=direction,
        )
        return MoveResponse(move=direction)
    except Exception:
        log.exception()
        raise HTTPException(status_code=404)


@api_router.post("/end")
def game_over(_: SnakeRequest) -> None:
    pass


api.include_router(api_router, dependencies=[Depends(log_request_info)])

# TODO: If the battlesnake is going to run out of health and die, take this into account with probabilities
# TODO: If the battlesnake consistently times out, take this into account with probabilities
