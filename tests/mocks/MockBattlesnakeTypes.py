from typing import List, Optional, Tuple
import uuid
from battle_python.BattlesnakeTypes import (
    Battlesnake,
    BattlesnakeCustomizations,
    Board,
    Coord,
    Game,
    Ruleset,
)


def get_mock_standard_game(
    foodSpawnChance: int = 15,
    minimumFood: int = 1,
    hazardDamagePerTurn: int = 14,
    timeout: int = 500,
) -> Game:
    return Game(
        id=str(uuid.uuid4()),
        ruleset=Ruleset(
            name="standard",
            version="v1.1.15",
            settings={
                "foodSpawnChance": foodSpawnChance,
                "minimumFood": minimumFood,
                "hazardDamagePerTurn": hazardDamagePerTurn,
            },
        ),
        map="standard",
        source="custom",
        timeout=timeout,
    )


def get_mock_standard_board(
    food_coords: Optional[List[Tuple[int, int]]] = None,
    hazard_coords: Optional[List[Tuple[int, int]]] = None,
    snakes: Optional[List[Battlesnake]] = None,
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
    body_coords: List[Tuple[int, int]],
    health: int = 60,
    latency: int = 456,
    turn: int = 0,
    board_width=0,
    board_height=0,
) -> Battlesnake:
    id = str(uuid.uuid4())
    body = [Coord(x=x, y=y) for x, y in body_coords]
    return Battlesnake(
        id=id,
        name=f"mock_battlesnake_{id}",
        health=health,
        body=body,
        latency=str(latency),
        head=body[0],
        length=len(body),
        shout="something to shout",
        customizations=BattlesnakeCustomizations(
            color="#888888", head="all-seeing", tail="curled"
        ),
        turn=turn,
        board_width=board_width,
        board_height=board_height,
    )
