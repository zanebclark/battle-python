import uuid
from battle_python.api_types import (
    SnakeCustomizations,
    Coord,
    Game,
    Ruleset,
    Board,
    Snake,
    SnakeRequest,
)


def get_mock_standard_game(
    food_spawn_chance: int = 10,
    minimum_food: int = 20,
    hazard_damage_per_turn: int = 30,
    timeout: int = 500,
) -> Game:
    return Game(
        id=str(uuid.uuid4()),
        ruleset=Ruleset(
            name="standard",
            version="v1.1.15",
            settings={
                "foodSpawnChance": food_spawn_chance,
                "minimumFood": minimum_food,
                "hazardDamagePerTurn": hazard_damage_per_turn,
            },
        ),
        map="standard",
        source="custom",
        timeout=timeout,
    )


def get_mock_snake(
    body_coords: tuple[Coord, ...],
    snake_id: str | None = None,
    health: int = 60,
    latency: int = 456,
) -> Snake:
    if snake_id is None:
        snake_id = str(uuid.uuid4())
    if not isinstance(body_coords[0], Coord):
        body_coords = tuple((Coord(x=x, y=y) for x, y in body_coords))
    return Snake(
        id=snake_id,
        name=f"mock_battlesnake_{snake_id}",
        health=health,
        body=body_coords,
        latency=str(latency),
        head=body_coords[0],
        length=len(body_coords),
        shout="something to shout",
        customizations=SnakeCustomizations(
            color="#888888", head="all-seeing", tail="curled"
        ),
    )


def get_mock_board(
    food_coords: tuple[Coord, ...] = tuple(),
    hazard_coords: tuple[Coord, ...] = tuple(),
    snakes: tuple[Snake, ...] | None = None,
    board_height: int = 11,
    board_width: int = 11,
) -> Board:
    if not snakes:
        snakes = []

    return Board(
        height=board_height,
        width=board_width,
        food=food_coords,
        hazards=hazard_coords,
        snakes=snakes,
    )


def get_mock_snake_request(
    turn: int,
    food_coords: tuple[Coord, ...] = tuple(),
    hazard_coords: tuple[Coord, ...] = tuple(),
    snakes: tuple[Snake, ...] | None = None,
    board_height: int = 11,
    board_width: int = 11,
    food_spawn_chance: int = 15,
    minimum_food: int = 1,
    hazard_damage_per_turn: int = 14,
    timeout: int = 500,
) -> SnakeRequest:
    game = get_mock_standard_game(
        food_spawn_chance=food_spawn_chance,
        minimum_food=minimum_food,
        hazard_damage_per_turn=hazard_damage_per_turn,
        timeout=timeout,
    )

    board = get_mock_board(
        food_coords=food_coords,
        hazard_coords=hazard_coords,
        snakes=snakes,
        board_height=board_height,
        board_width=board_width,
    )

    return SnakeRequest(
        game=game,
        turn=turn,
        board=board,
        you=snakes[0],
    )
