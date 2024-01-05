import uuid
from battle_python.api_types import (
    BattlesnakeCustomizations,
    Coord,
    Game,
    Ruleset,
    Board,
    Battlesnake,
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
    height: int = 11,
    width: int = 11,
) -> Board:
    if not food_coords:
        food_coords = []
    if not hazard_coords:
        hazard_coords = []
    if not snakes:
        snakes = []

    food = [Coord(x=x, y=y) for x, y in food_coords if food_coords is not None]
    hazards = [Coord(x=x, y=y) for x, y in hazard_coords if hazard_coords is not None]

    return Board(height=height, width=width, food=food, hazards=hazards, snakes=snakes)


def get_mock_battlesnake(
    body_coords: list[tuple[int, int]], health: int = 60, latency: int = 456
) -> Battlesnake:
    id_value = str(uuid.uuid4())
    body = [Coord(x=x, y=y) for x, y in body_coords]
    return Battlesnake(
        id=id_value,
        name=f"mock_battlesnake_{id_value}",
        health=health,
        body=body,
        latency=str(latency),
        head=body[0],
        length=len(body),
        shout="something to shout",
        customizations=BattlesnakeCustomizations(
            color="#888888", head="all-seeing", tail="curled"
        ),
    )
