import random
import time

from src.cards import load_bands
from src.collection import spend_coins, add_band

RARITY_WEIGHTS = {
    "Common": 50,
    "Uncommon": 25,
    "Rare": 15,
    "Epic": 7,
    "Legendary": 3,
}

PACK_COST = 300
MAX_PACKS = 5
REGEN_INTERVAL_SECONDS = 12 * 60  # 1 new pack every 12 minutes
DAILY_COOLDOWN_SECONDS = 24 * 60 * 60

PACKS = {
    "heavy_metal": {"display_name": "Heavy Metal Pack", "cost": PACK_COST},
    "thrash_metal": {"display_name": "Thrash Metal Pack", "cost": PACK_COST},
    "death_metal": {"display_name": "Death Metal Pack", "cost": PACK_COST},
    "black_metal": {"display_name": "Black Metal Pack", "cost": PACK_COST},
    "metalcore": {"display_name": "Metalcore Pack", "cost": PACK_COST},
    "nu_metal": {"display_name": "Nu Metal Pack", "cost": PACK_COST},
    "power_metal": {"display_name": "Power Metal Pack", "cost": PACK_COST},
    "doom_metal": {"display_name": "Doom Metal Pack", "cost": PACK_COST},
    "progressive_metal": {"display_name": "Progressive Metal Pack", "cost": PACK_COST},
    "deathcore": {"display_name": "Deathcore Pack", "cost": PACK_COST},
    "alternative_metal": {"display_name": "Alternative Metal Pack", "cost": PACK_COST},
    "glam_metal": {"display_name": "Glam Metal Pack", "cost": PACK_COST},
    "folk_metal": {"display_name": "Folk Metal Pack", "cost": PACK_COST},
    "gothic_metal": {"display_name": "Gothic Metal Pack", "cost": PACK_COST},
    "speed_metal": {"display_name": "Speed Metal Pack", "cost": PACK_COST},
    "melodic_death_metal": {"display_name": "Melodic Death Metal Pack", "cost": PACK_COST},
    "djent": {"display_name": "Djent Pack", "cost": PACK_COST},
    "technical_death_metal": {"display_name": "Technical Death Metal Pack", "cost": PACK_COST},
    "industrial_metal": {"display_name": "Industrial Metal Pack", "cost": PACK_COST},
    "symphonic_metal": {"display_name": "Symphonic Metal Pack", "cost": PACK_COST},
}


def _regen_packs(player: dict) -> None:
    """Regenerate packs based on elapsed time, keeping the next regen timestamp valid."""
    available = player.get("packs_available", MAX_PACKS)
    next_regen = player.get("next_pack_regen", 0)
    now = time.time()

    # Already full: schedule the next regeneration in the future.
    if available >= MAX_PACKS:
        player["packs_available"] = MAX_PACKS
        player["next_pack_regen"] = now + REGEN_INTERVAL_SECONDS
        return

    # No regeneration timestamp yet.
    if next_regen <= 0:
        player["packs_available"] = available
        player["next_pack_regen"] = now + REGEN_INTERVAL_SECONDS
        return

    # Regenerate all packs that have accumulated.
    while now >= next_regen and available < MAX_PACKS:
        available += 1
        next_regen += REGEN_INTERVAL_SECONDS

    player["packs_available"] = available

    # If we reached the maximum, the old timestamp may still be in the past.
    # Reset it so that the next consumed pack gets a fresh 12-minute timer.
    if available >= MAX_PACKS:
        player["next_pack_regen"] = now + REGEN_INTERVAL_SECONDS
    else:
        player["next_pack_regen"] = next_regen

def get_remaining_packs(player: dict) -> int:
    _regen_packs(player)
    return player["packs_available"]


def get_seconds_until_next_pack(player: dict) -> int:
    _regen_packs(player)
    if player["packs_available"] >= MAX_PACKS:
        return 0
    return max(0, int(player["next_pack_regen"] - time.time()))


def format_countdown(seconds: int) -> str:
    minutes, secs = divmod(seconds, 60)
    return f"{minutes}m {secs}s"


def get_pool(catalog: list[dict], pack_type: str) -> list[dict]:
    return [band for band in catalog if band["pack_type"] == pack_type]


def draw_band(pool: list[dict]) -> dict:
    weights = [RARITY_WEIGHTS.get(band["rarity"], 1) for band in pool]
    return random.choices(pool, weights=weights, k=1)[0]


def open_pack(pack_type: str, player: dict) -> dict | str:
    """
    Try to open a pack. Returns {'band': ..., 'is_new': bool} on success,
    or an error message string on failure. Never draws a band the player
    already owns — if the whole pool is already owned, the pack is blocked
    (and no coins are spent).
    """
    if pack_type not in PACKS:
        return f"Unknown pack type: {pack_type}"

    _regen_packs(player)
    if player["packs_available"] <= 0:
        wait = format_countdown(get_seconds_until_next_pack(player))
        return f"No packs available right now. Next one in {wait}."

    pack = PACKS[pack_type]
    catalog = load_bands()
    full_pool = get_pool(catalog, pack_type)

    if not full_pool:
        return f"No bands available for pack type '{pack_type}' yet."

    owned_ids = set(player["collection"])
    pool = [band for band in full_pool if band["id"] not in owned_ids]

    if not pool:
        genre_name = pack["display_name"].replace(" Pack", "")
        return f"You already own every {genre_name} band!"

    if not spend_coins(player, pack["cost"]):
        return f"Not enough coins. {pack['display_name']} costs {pack['cost']} coins."

    drawn = draw_band(pool)
    add_band(player, drawn["id"])
    player["packs_available"] -= 1

    return {"band": drawn, "is_new": True}


def can_claim_daily(player: dict) -> bool:
    last = player.get("last_daily_claim", 0)
    return time.time() - last >= DAILY_COOLDOWN_SECONDS


def get_seconds_until_daily(player: dict) -> int:
    last = player.get("last_daily_claim", 0)
    remaining = DAILY_COOLDOWN_SECONDS - (time.time() - last)
    return max(0, int(remaining))


def claim_daily(player: dict) -> dict | str:
    """
    Claim the free daily band, from any genre in the catalog.
    Returns {'band': ..., 'is_new': bool} on success, or an error message.
    """
    if not can_claim_daily(player):
        wait = get_seconds_until_daily(player)
        hours, remainder = divmod(wait, 3600)
        minutes = remainder // 60
        return f"You already claimed today's free pack. Next one in {hours}h {minutes}m."

    catalog = load_bands()
    drawn = draw_band(catalog)
    is_new = drawn["id"] not in player["collection"]
    add_band(player, drawn["id"])
    player["last_daily_claim"] = time.time()

    return {"band": drawn, "is_new": is_new}


def get_pool_hint(player: dict, catalog: list[dict]) -> str | None:
    """Suggest a pack type that hasn't given the player a Legendary yet."""
    owned_ids = set(player["collection"])
    candidates = []

    for pack_type, pack in PACKS.items():
        pool = get_pool(catalog, pack_type)
        if not pool:
            continue
        pool_has_legendary = any(b["rarity"] == "Legendary" for b in pool)
        already_got_one = any(
            b["rarity"] == "Legendary" and b["id"] in owned_ids for b in pool
        )
        if pool_has_legendary and not already_got_one:
            candidates.append(pack["display_name"])

    if not candidates:
        return None
    return random.choice(candidates)