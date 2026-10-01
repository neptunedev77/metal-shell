import random

RARITY_WEIGHTS = {
    "Common": 50,
    "Uncommon": 25,
    "Rare": 15,
    "Epic": 7,
    "Legendary": 3,
}


def generate_bot_team(catalog: list[dict]) -> list[dict]:
    """Pick 3 distinct random bands from the whole catalog, weighted by rarity."""
    pool = catalog.copy()
    team = []
    for _ in range(3):
        weights = [RARITY_WEIGHTS.get(b["rarity"], 1) for b in pool]
        pick = random.choices(pool, weights=weights, k=1)[0]
        team.append(pick)
        pool.remove(pick)
    return team


def choose_band(alive_bot_bands: list[dict], attribute: str) -> dict:
    """
    Pick a band for the BOT to use this round.
    70% of the time: the best option for this attribute.
    30% of the time: a random alive band (keeps the BOT unpredictable).
    """
    if random.random() < 0.7:
        return max(alive_bot_bands, key=lambda b: b["band"]["attributes"][attribute])
    return random.choice(alive_bot_bands)