import json
from pathlib import Path
import time

PLAYER_PATH = Path(__file__).resolve().parent.parent / "data" / "player.json"

SELL_VALUES = {
    "Common": 20,
    "Uncommon": 40,
    "Rare": 80,
    "Epic": 150,
    "Legendary": 300,
}

INCOME_AMOUNT = 10          # coins per minute
INCOME_INTERVAL_SECONDS = 60
MAX_INCOME_MINUTES = 120    # cap: at most 2 hours of accumulated income at once

def load_player(path: Path = PLAYER_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_player(player: dict, path: Path = PLAYER_PATH) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(player, f, indent=2, ensure_ascii=False)


def get_owned_bands(player: dict, catalog: list[dict]) -> list[dict]:
    """Cross-reference the player's owned band IDs with the full catalog data."""
    owned_ids = set(player["collection"])
    return [band for band in catalog if band["id"] in owned_ids]


def add_band(player: dict, band_id: str) -> None:
    player["collection"].append(band_id)


def remove_band(player: dict, band_id: str) -> bool:
    """Remove one copy of a band from the collection. Returns True if removed."""
    if band_id in player["collection"]:
        player["collection"].remove(band_id)
        return True
    return False


def add_coins(player: dict, amount: int) -> None:
    player["coins"] += amount


def spend_coins(player: dict, amount: int) -> bool:
    """Try to spend coins. Returns True if successful, False if insufficient balance."""
    if player["coins"] < amount:
        return False
    player["coins"] -= amount
    return True


def set_team(player: dict, band_ids: list[str]) -> None:
    player["team"] = band_ids


def get_team_bands(player: dict, catalog: list[dict]) -> list[dict]:
    """Return full band data for the bands currently in the player's team, in order."""
    catalog_by_id = {band["id"]: band for band in catalog}
    return [catalog_by_id[bid] for bid in player.get("team", []) if bid in catalog_by_id]

def regen_income(player: dict) -> int:
    """
    Add passive coins based on elapsed time (works even while the game is
    closed). Returns how many coins were just added (0 if none yet).
    """
    now = time.time()
    next_tick = player.get("next_income_tick", 0)

    if next_tick == 0:
        player["next_income_tick"] = now + INCOME_INTERVAL_SECONDS
        return 0

    if now < next_tick:
        return 0

    elapsed = now - next_tick
    minutes_passed = int(elapsed // INCOME_INTERVAL_SECONDS) + 1
    minutes_capped = min(minutes_passed, MAX_INCOME_MINUTES)

    earned = minutes_capped * INCOME_AMOUNT
    player["coins"] += earned

    if minutes_passed > MAX_INCOME_MINUTES:
        player["next_income_tick"] = now + INCOME_INTERVAL_SECONDS
    else:
        player["next_income_tick"] = next_tick + minutes_passed * INCOME_INTERVAL_SECONDS

    return earned

def has_rarity(player: dict, catalog: list[dict], rarity: str) -> bool:
    """Check whether the player already owns at least one band of this rarity."""
    owned_ids = set(player["collection"])
    return any(
        band["rarity"] == rarity and band["id"] in owned_ids for band in catalog
    )