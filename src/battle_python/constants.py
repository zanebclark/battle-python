import numpy as np

from battle_python.api_types import Coord

MANHATTAN_MOVES = np.array(
    [
        [False, True, False],
        [True, False, True],
        [False, True, False],
    ]
)
DEATH_SCORE = -1000
WIN_SCORE = abs(DEATH_SCORE)
FOOD_SCORE = 100
MURDER_SCORE = 100
DEATH_COORD = Coord(x=1000, y=1000)
FOOD_WEIGHT = 5
AREA_MULTIPLIER = 1
CENTER_CONTROL_WEIGHT = 2
