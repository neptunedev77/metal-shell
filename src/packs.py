import random

from src.cards import load_bands
from src.collection import spend_coins, add_band

RARITY_WEIGHTS = {
    "Common": 50,
    "Uncommon": 25,
    "Rare": 15,
    "Epic": 7,
    "Legendary": 3,
}

PACKS = {
    "heavy_metal": {"display_name": "Heavy Metal Pack", "cost": 100},
    "thrash_metal": {"display_name": "Thrash Metal Pack", "cost": 100},
    "death_metal": {"display_name": "Death Metal Pack", "cost": 100},
    "black_metal": {"display_name": "Black Metal Pack", "cost": 100},
    "metalcore": {"display_name": "Metalcore Pack", "cost": 100},
    "nu_metal": {"display_name": "Nu Metal Pack", "cost": 100},
    "power_metal": {"display_name": "Power Metal Pack", "cost": 100},
    "doom_metal": {"display_name": "Doom Metal Pack", "cost": 100},
    "progressive_metal": {"display_name": "Progressive Metal Pack", "cost": 100},
    "deathcore": {"display_name": "Deathcore Pack", "cost": 100},
    "alternative_metal": {"display_name": "Alternative Metal Pack", "cost": 100},
    "glam_metal": {"display_name": "Glam Metal Pack", "cost": 100},
    "folk_metal": {"display_name": "Folk Metal Pack", "cost": 100},
    "gothic_metal": {"display_name": "Gothic Metal Pack", "cost": 100},
    "speed_metal": {"display_name": "Speed Metal Pack", "cost": 100},
    "melodic_death_metal": {"display_name": "Melodic Death Metal Pack", "cost": 100},
    "djent": {"display_name": "Djent Pack", "cost": 100},
    "technical_death_metal": {"display_name": "Technical Death Metal Pack", "cost": 100},
    "industrial_metal": {"display_name": "Industrial Metal Pack", "cost": 100},
    "symphonic_metal": {"display_name": "Symphonic Metal Pack", "cost": 100},
}


def get_pool(catalog: list[dict], pack_type: str) -> list[dict]:
    """Return only the bands that belong to this pack type."""
    return [band for band in catalog if band["pack_type"] == pack_type]


def draw_band(pool: list[dict]) -> dict:
    """Pick one band from the pool, weighted by rarity."""
    weights = [RARITY_WEIGHTS.get(band["rarity"], 1) for band in pool]
    return random.choices(pool, weights=weights, k=1)[0]


def open_pack(pack_type: str, player: dict) -> list[dict] | str:
    """
    Try to open a pack. Returns a list of 3 drawn bands on success,
    or an error message string on failure.
    """
    if pack_type not in PACKS:
        return f"Unknown pack type: {pack_type}"

    pack = PACKS[pack_type]
    catalog = load_bands()
    pool = get_pool(catalog, pack_type)

    if not pool:
        return f"No bands available for pack type '{pack_type}' yet."

    if not spend_coins(player, pack["cost"]):
        return f"Not enough coins. {pack['display_name']} costs {pack['cost']} coins."

    drawn = [draw_band(pool) for _ in range(3)]
    for band in drawn:
        add_band(player, band["id"])

    return drawn