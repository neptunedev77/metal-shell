"""
Validate data/bands.json.

Run from the project root:
    python -m src.validate_bands
    python -m src.validate_bands path/to/other.json

Exit code is 1 if any ERROR is found (warnings do not fail the check).
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

from src.cards import DATA_PATH
from src.config import RARITY_WEIGHTS
from src.packs import PACKS

REQUIRED_FIELDS = ["id", "name", "genre", "pack_type", "rarity", "attributes"]
REQUIRED_ATTRIBUTES = ["riffs", "vocals", "drums", "heaviness", "atmosphere", "popularity"]
ATTR_MIN, ATTR_MAX = 0, 100
ID_PATTERN = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")

# Words used as keywords by $sell, so no band may be called like this.
RESERVED_WORDS = {"all", "rarity"}

# Current data convention: rarity follows popularity (not combat strength).
# Used only to raise warnings, so a new band with a mismatched value is noticed.
POPULARITY_RANGES = {
    "Common": (0, 63),
    "Uncommon": (64, 74),
    "Rare": (75, 84),
    "Epic": (85, 92),
    "Legendary": (93, 100),
}


def _label(index: int, band) -> str:
    bid = band.get("id") if isinstance(band, dict) else None
    return f"#{index} ({bid})" if bid else f"#{index}"


def validate_bands(bands: list) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(bands, list):
        return ["Top-level JSON must be a list of bands."], []

    valid_rarities = set(RARITY_WEIGHTS)
    genre_by_pack = {
        key: pack["display_name"].removesuffix(" Pack") for key, pack in PACKS.items()
    }

    for i, band in enumerate(bands):
        if not isinstance(band, dict):
            errors.append(f"#{i}: band is not an object.")
            continue
        tag = _label(i, band)

        # required fields
        missing = [f for f in REQUIRED_FIELDS if f not in band]
        if missing:
            errors.append(f"{tag}: missing fields {missing}")
        extra = [f for f in band if f not in REQUIRED_FIELDS]
        if extra:
            warnings.append(f"{tag}: unexpected fields {extra}")

        # id
        bid = band.get("id")
        if "id" in band:
            if not isinstance(bid, str) or not ID_PATTERN.match(bid):
                errors.append(f"{tag}: invalid id {bid!r} (use lowercase_snake_case)")
            elif bid in RESERVED_WORDS:
                errors.append(f"{tag}: id {bid!r} is a reserved word")

        # name
        name = band.get("name")
        if "name" in band:
            if not isinstance(name, str) or not name.strip():
                errors.append(f"{tag}: empty or invalid name {name!r}")
            elif name != name.strip():
                errors.append(f"{tag}: name has leading/trailing spaces {name!r}")
            elif "," in name:
                errors.append(f"{tag}: name contains a comma, which breaks $team/$sell parsing")
            elif name.lower() in RESERVED_WORDS:
                errors.append(f"{tag}: name {name!r} is a reserved word")
            elif len(name) > 30:
                warnings.append(f"{tag}: name longer than 30 chars may break the card layout")

        # rarity
        if "rarity" in band and band["rarity"] not in valid_rarities:
            errors.append(f"{tag}: invalid rarity {band['rarity']!r} (valid: {sorted(valid_rarities)})")

        # pack_type + genre consistency
        pack_type = band.get("pack_type")
        if "pack_type" in band and pack_type not in PACKS:
            errors.append(f"{tag}: unknown pack_type {pack_type!r}")
        elif pack_type in genre_by_pack and "genre" in band and band["genre"] != genre_by_pack[pack_type]:
            warnings.append(
                f"{tag}: genre {band['genre']!r} does not match pack {pack_type!r} "
                f"(expected {genre_by_pack[pack_type]!r})"
            )

        # attributes
        attrs = band.get("attributes")
        if "attributes" in band:
            if not isinstance(attrs, dict):
                errors.append(f"{tag}: attributes must be an object")
            else:
                for a in REQUIRED_ATTRIBUTES:
                    if a not in attrs:
                        errors.append(f"{tag}: missing attribute {a!r}")
                for a in attrs:
                    if a not in REQUIRED_ATTRIBUTES:
                        errors.append(f"{tag}: unknown attribute {a!r}")
                for a, v in attrs.items():
                    if isinstance(v, bool) or not isinstance(v, int):
                        errors.append(f"{tag}: attribute {a} must be an integer, got {v!r}")
                    elif not ATTR_MIN <= v <= ATTR_MAX:
                        errors.append(f"{tag}: attribute {a}={v} outside {ATTR_MIN}-{ATTR_MAX}")

                pop = attrs.get("popularity")
                rarity = band.get("rarity")
                if isinstance(pop, int) and not isinstance(pop, bool) and rarity in POPULARITY_RANGES:
                    lo, hi = POPULARITY_RANGES[rarity]
                    if not lo <= pop <= hi:
                        warnings.append(
                            f"{tag}: popularity {pop} is outside the usual range "
                            f"for {rarity} ({lo}-{hi})"
                        )

    # uniqueness
    ids = [b.get("id") for b in bands if isinstance(b, dict) and "id" in b]
    for bid, n in Counter(ids).items():
        if n > 1:
            errors.append(f"duplicate id {bid!r} ({n} times)")

    names = [b["name"].strip().lower() for b in bands
             if isinstance(b, dict) and isinstance(b.get("name"), str)]
    for name, n in Counter(names).items():
        if n > 1:
            errors.append(f"duplicate name {name!r} ({n} times)")

    # every pack needs at least one band, otherwise $open fails for it
    used = {b.get("pack_type") for b in bands if isinstance(b, dict)}
    for pack_type in PACKS:
        if pack_type not in used:
            errors.append(f"pack {pack_type!r} has no bands")

    return errors, warnings


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_PATH
    with open(path, "r", encoding="utf-8") as f:
        bands = json.load(f)

    errors, warnings = validate_bands(bands)

    print(f"Checked {len(bands)} bands in {path}")
    for w in warnings:
        print(f"  WARNING: {w}")
    for e in errors:
        print(f"  ERROR:   {e}")

    if errors:
        print(f"\nFAILED: {len(errors)} error(s), {len(warnings)} warning(s).")
        return 1
    print(f"\nOK: no errors, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
