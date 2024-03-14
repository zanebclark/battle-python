import os
import time
from typing import Literal

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    APIRouter,
    Depends,
    status,
    BackgroundTasks,
)
import structlog
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from battle_python.GameState import GameState
from battle_python.api_types import SnakeMetadataResponse, SnakeRequest, MoveResponse
from battle_python.dynamodb import GamesTable, RequestsTable
from battle_python.logging_config import configure_logger

configure_logger()
logger = structlog.get_logger()

RestMethod = Literal["GET", "POST"]
api = FastAPI(
    title="Battlesnake Webhook Handler",
    description="Webhook endpoints called by Battlesnakes.com to play the game",
    version="1.0",
    docs_url=None if os.environ.get("ENV") == "PROD" else "/docs",
)
api_router = APIRouter()


@api.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def log_request_info(request: Request) -> None:
    structlog.contextvars.clear_contextvars()
    request_body: dict = {}
    if request.url != request.base_url:
        request_body = await request.json()
        structlog.contextvars.bind_contextvars(
            game_id=request_body["game"]["id"],
            my_snake_id=request_body["you"]["id"],
            turn=request_body["turn"],
            request_nanoseconds=time.time_ns(),
        )
    logger.debug(
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
def game_started(
    request: SnakeRequest, games_table: GamesTable = Depends(GamesTable.factory)
) -> None:
    games_table.add_game(request=request)


@api_router.post("/move")
def move(
    move_request: SnakeRequest,
    background_tasks: BackgroundTasks,
    requests_table: RequestsTable = Depends(RequestsTable.factory),
) -> MoveResponse:
    request_nanoseconds = time.time_ns()
    request_milliseconds = int(str(request_nanoseconds)[:-6])

    try:
        gs = GameState.from_snake_request(move_request=move_request)
        direction, boards_explored, terminal_boards = gs.get_next_move(
            request_nanoseconds=request_nanoseconds
        )
        logger.debug(
            "returning move",
            move=direction,
        )
        background_tasks.add_task(
            requests_table.add_request,
            request=move_request,
            move=direction,
            latency=int(str(time.time_ns())[:-6]) - request_milliseconds,
            boards_explored=boards_explored,
            terminal_boards=terminal_boards,
            exception=False,
        )
        return MoveResponse(move=direction)
    except Exception:
        requests_table.add_request(request=move_request, exception=True)
        logger.exception("something went wrong")
        raise HTTPException(status_code=404)


@api_router.post("/end")
def game_over(
    request: SnakeRequest, games_table: GamesTable = Depends(GamesTable.factory)
) -> None:
    games_table.update_game(request=request)


api.include_router(api_router, dependencies=[Depends(log_request_info)])

# TODO: If the battlesnake is going to run out of health and die, take this into account with probabilities
# TODO: If the battlesnake consistently times out, take this into account with probabilities
# TODO: Anticipate hazard progression
