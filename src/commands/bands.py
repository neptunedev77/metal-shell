from src.cards import load_bands, format_card, format_band_list
from src.collection import get_owned_bands
from src.packs import PACKS
from src.commands.common import get_fresh_player


def cmd_bands(args: list[str]) -> None:
    catalog = load_bands()
    player = get_fresh_player()
    owned = get_owned_bands(player, catalog)

    if not owned:
        print("Your collection is empty. You don't own any bands yet.")
        return

    print(format_band_list(owned))


def cmd_band(args: list[str]) -> None:
    if not args:
        print("Usage: $band <name>")
        return

    catalog = load_bands()
    player = get_fresh_player()
    owned = get_owned_bands(player, catalog)

    query = " ".join(args).lower()
    match = next(
        (b for b in owned if b["name"].lower() == query or b["id"].lower() == query),
        None,
    )
    if match is None:
        print(f"You don't own a band called '{' '.join(args)}'.")
        return
    print(format_card(match))


def cmd_progress(args: list[str]) -> None:
    catalog = load_bands()
    player = get_fresh_player()

    owned_ids = set(player["collection"])

    total_bands = len(catalog)
    collected = sum(1 for band in catalog if band["id"] in owned_ids)

    print("\nCOLLECTION")
    print(f"  {collected} / {total_bands} bands")

    percentage = (collected / total_bands * 100) if total_bands else 0
    print(f"  Overall: {percentage:.0f}%")

    # Rarity progress
    rarities = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]

    print("\nBY RARITY")

    for rarity in rarities:
        total = sum(
            1 for band in catalog
            if band["rarity"] == rarity
        )

        owned = sum(
            1 for band in catalog
            if band["rarity"] == rarity
            and band["id"] in owned_ids
        )

        print(f"  {rarity:<11} {owned:>2} / {total}")

    # Pack progress
    print("\nBY PACK")

    for pack_type, pack in PACKS.items():
        pack_bands = [
            band for band in catalog
            if band["pack_type"] == pack_type
        ]

        if not pack_bands:
            continue

        total = len(pack_bands)
        owned = sum(
            1 for band in pack_bands
            if band["id"] in owned_ids
        )

        print(f"  {pack['display_name']:<28} {owned:>2} / {total}")

    print()


def cmd_coins(args: list[str]) -> None:
    player = get_fresh_player()
    print(f"Coins: {player['coins']}")
