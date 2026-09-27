import json
from pathlib import Path

PLAYER_PATH = Path(__file__).resolve().parent.parent / "data" / "player.json"


def load_player(path: Path = PLAYER_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_player(player: dict, path: Path = PLAYER_PATH) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(player, f, indent=2, ensure_ascii=False)


def get_owned_bands(player: dict, catalog: list[dict]) -> list[dict]:
    """Cruza os IDs da coleccao do jogador com os dados completos do catalogo."""
    owned_ids = set(player["collection"])
    return [band for band in catalog if band["id"] in owned_ids]


def add_band(player: dict, band_id: str) -> None:
    player["collection"].append(band_id)


def add_coins(player: dict, amount: int) -> None:
    player["coins"] += amount


def spend_coins(player: dict, amount: int) -> bool:
    """Tenta gastar coins. Devolve True se conseguiu, False se nao tem saldo."""
    if player["coins"] < amount:
        return False
    player["coins"] -= amount
    return True
