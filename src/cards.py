import json
from pathlib import Path

RARITY_STARS = {
    "Common": "★☆☆☆☆",
    "Uncommon": "★★☆☆☆",
    "Rare": "★★★☆☆",
    "Epic": "★★★★☆",
    "Legendary": "★★★★★",
}

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "bands.json"


def load_bands(path: Path = DATA_PATH) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_card(band: dict) -> str:
    width = 32
    lines = ["╔" + "═" * width + "╗"]
    lines.append(f"║{band['name'].upper().center(width)}║")
    lines.append(f"║{band['genre'].center(width)}║")
    lines.append("╠" + "═" * width + "╣")

    for attr_name, value in band["attributes"].items():
        if attr_name == "popularity":
            continue
        label = attr_name.capitalize()
        row = f" {label:<14}{value:<15}"
        lines.append(f"║{row[:width]}║")

    lines.append("╠" + "═" * width + "╣")
    stars = RARITY_STARS.get(band["rarity"], "?????")
    row = f" Rarity        {stars}"
    lines.append(f"║{row[:width].ljust(width)}║")
    lines.append("╚" + "═" * width + "╝")

    return "\n".join(lines)


def format_band_list(bands: list[dict]) -> str:
    """Format a list of bands in compact form, one line per band."""
    lines = []
    for band in bands:
        stars = RARITY_STARS.get(band["rarity"], "?????")
        lines.append(f"{band['name']:<20} {band['genre']:<28} {stars}")
    return "\n".join(lines)