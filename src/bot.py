import random

from src.battle import ATTRIBUTES
from src.config import RARITY_WEIGHTS


def combat_average(band: dict) -> float:
    """Average of the combat attributes (popularity excluded)."""
    return sum(band["attributes"][a] for a in ATTRIBUTES) / len(ATTRIBUTES)


def generate_bot_team(
    catalog: list[dict],
    candidates: int = 3,
    pick: str = "random",
) -> list[dict]:
    """
    Draw `candidates` distinct bands from the whole catalog (weighted by rarity),
    then keep 3 of them:
      - "random":    the first 3 drawn (with candidates=3 this is the original behaviour)
      - "weakest":   the 3 with the lowest average combat stats
      - "strongest": the 3 with the highest average combat stats

    Rarity follows popularity, not strength, so strength is judged by the
    combat attributes instead of the rarity.
    """
    candidates = max(3, min(candidates, len(catalog)))
    pool = catalog.copy()
    drawn = []
    for _ in range(candidates):
        weights = [RARITY_WEIGHTS.get(b["rarity"], 1) for b in pool]
        choice = random.choices(pool, weights=weights, k=1)[0]
        drawn.append(choice)
        pool.remove(choice)

    if pick == "weakest":
        drawn.sort(key=combat_average)
    elif pick == "strongest":
        drawn.sort(key=combat_average, reverse=True)

    return drawn[:3]


def choose_band(
    alive_bot_bands: list[dict],
    attribute: str,
    smart_chance: float = 0.7,
) -> dict:
    """
    Pick a band for the BOT to use this round.
    `smart_chance` of the time: the best option for this attribute.
    Otherwise: a random alive band (keeps the BOT unpredictable).
    """
    if random.random() < smart_chance:
        return max(alive_bot_bands, key=lambda b: b["band"]["attributes"][attribute])
    return random.choice(alive_bot_bands)
