import uuid
from battle_python.api_types import (
    BattlesnakeCustomizations,
    Coord,
    Game,
    Ruleset,
    Board,
    Battlesnake,
    GameState,
)


def get_mock_standard_game(
    food_spawn_chance: int = 15,
    minimum_food: int = 1,
    hazard_damage_per_turn: int = 14,
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


def get_mock_standard_board(
    food_coords: list[tuple[int, int]] | None = None,
    hazard_coords: list[tuple[int, int]] | None = None,
    snakes: list[Battlesnake] | None = None,
    board_height: int = 11,
    board_width: int = 11,
) -> Board:
    if not food_coords:
        food_coords = []
    if not hazard_coords:
        hazard_coords = []
    if not snakes:
        snakes = []

    food = [Coord(x=x, y=y) for x, y in food_coords if food_coords is not None]
    hazards = [Coord(x=x, y=y) for x, y in hazard_coords if hazard_coords is not None]

    return Board(
        height=board_height,
        width=board_width,
        food=food,
        hazards=hazards,
        snakes=snakes,
    )


def get_mock_battlesnake(
    body_coords: list[tuple[int, int]] | list[Coord],
    snake_id: str | None = None,
    health: int = 60,
    latency: int = 456,
    is_self: bool = False,
) -> Battlesnake:
    if snake_id is None:
        snake_id = str(uuid.uuid4())
    if not isinstance(body_coords[0], Coord):
        body_coords = [Coord(x=x, y=y) for x, y in body_coords]
    return Battlesnake(
        id=snake_id,
        is_self=is_self,
        name=f"mock_battlesnake_{snake_id}",
        health=health,
        body=body_coords,
        latency=str(latency),
        head=body_coords[0],
        length=len(body_coords),
        shout="something to shout",
        customizations=BattlesnakeCustomizations(
            color="#888888", head="all-seeing", tail="curled"
        ),
    )


def get_mock_gamestate(
    turn: int,
    food_coords: list[tuple[int, int]] | None = None,
    hazard_coords: list[tuple[int, int]] | None = None,
    snakes: list[Battlesnake] | None = None,
    board_height: int = 11,
    board_width: int = 11,
    food_spawn_chance: int = 15,
    minimum_food: int = 1,
    hazard_damage_per_turn: int = 14,
    timeout: int = 500,
) -> GameState:
    game = get_mock_standard_game(
        food_spawn_chance=food_spawn_chance,
        minimum_food=minimum_food,
        hazard_damage_per_turn=hazard_damage_per_turn,
        timeout=timeout,
    )

    board = get_mock_standard_board(
        food_coords=food_coords,
        hazard_coords=hazard_coords,
        snakes=snakes,
        board_height=board_height,
        board_width=board_width,
    )

    yous = [snake for snake in snakes if snake.is_self]
    if len(yous) != 1:
        raise Exception(f"There can only be one!\n\n{yous}")

    return GameState(
        game=game,
        turn=turn,
        board=board,
        you=yous[0],
    )
