import json
from pathlib import Path

RARITY_STARS = {
    "Common": "\u2605\u2606\u2606\u2606\u2606",
    "Uncommon": "\u2605\u2605\u2606\u2606\u2606",
    "Rare": "\u2605\u2605\u2605\u2606\u2606",
    "Epic": "\u2605\u2605\u2605\u2605\u2606",
    "Legendary": "\u2605\u2605\u2605\u2605\u2605",
}

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "bands.json"


def load_bands(path: Path = DATA_PATH) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_card(band: dict) -> str:
    width = 32
    lines = ["\u2554" + "\u2550" * width + "\u2557"]
    lines.append(f"\u2551{band['name'].upper().center(width)}\u2551")
    lines.append(f"\u2551{band['genre'].center(width)}\u2551")
    lines.append("\u2560" + "\u2550" * width + "\u2563")

    for attr_name, value in band["attributes"].items():
        if attr_name == "popularity":
            continue
        label = attr_name.capitalize()
        row = f" {label:<14}{value:<15}"
        lines.append(f"\u2551{row[:width]}\u2551")

    lines.append("\u2560" + "\u2550" * width + "\u2563")
    stars = RARITY_STARS.get(band["rarity"], "?????")
    row = f" Rarity        {stars}"
    lines.append(f"\u2551{row[:width].ljust(width)}\u2551")
    lines.append("\u255a" + "\u2550" * width + "\u255d")

    return "\n".join(lines)


def format_band_list(bands: list[dict]) -> str:
    """Formata uma lista de bandas em formato compacto, uma linha por banda."""
    lines = []
    for band in bands:
        stars = RARITY_STARS.get(band["rarity"], "?????")
        lines.append(f"{band['name']:<20} {band['genre']:<28} {stars}")
    return "\n".join(lines)
