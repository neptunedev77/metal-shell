from collections import defaultdict
from pathlib import Path
import json

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


def best_attribute(band: dict) -> tuple[str, int]:
    """Return the (name, value) of the highest combat attribute, excluding popularity."""
    combat_attrs = {k: v for k, v in band["attributes"].items() if k != "popularity"}
    name = max(combat_attrs, key=combat_attrs.get)
    return name.capitalize(), combat_attrs[name]


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
        lines.append(f"║{row[:width].ljust(width)}║")

    lines.append("╠" + "═" * width + "╣")
    stars = RARITY_STARS.get(band["rarity"], "?????")
    row = f" Rarity        {stars}"
    lines.append(f"║{row[:width].ljust(width)}║")
    lines.append("╚" + "═" * width + "╝")

    return "\n".join(lines)


def format_band_list(bands: list[dict]) -> str:
    """Group bands by genre (alphabetical), sorted by name within each genre."""
    groups = defaultdict(list)
    for band in bands:
        groups[band["genre"]].append(band)

    id_width = max((len(b["id"]) for b in bands), default=0) + 2
    name_width = max((len(b["name"]) for b in bands), default=0) + 2

    lines = []
    for genre in sorted(groups.keys()):
        lines.append(f"\n{genre}")
        lines.append("-" * len(genre))
        for band in sorted(groups[genre], key=lambda b: b["name"]):
            stars = RARITY_STARS.get(band["rarity"], "?????")
            attr_name, attr_value = best_attribute(band)
            lines.append(
                f"  {band['id']:<{id_width}}{band['name']:<{name_width}}{stars:<10}best: {attr_name} {attr_value}"
            )

    return "\n".join(lines).strip("\n")