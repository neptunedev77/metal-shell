from src.cards import load_bands
from src.collection import (
    save_player, get_owned_bands, add_coins, remove_band, SELL_VALUES,
    sell_bands, get_bands_by_rarity, remove_bands_from_team,
)
from src.commands.common import get_fresh_player


def check_team_conflict(player: dict, bands_to_sell: list[dict]) -> bool:
    """
    If any band about to be sold is in the current team, warn and ask for
    confirmation. Returns True if the sale should proceed.
    """
    team_ids = set(player.get("team", []))
    conflicts = [b for b in bands_to_sell if b["id"] in team_ids]
    if not conflicts:
        return True

    names = ", ".join(b["name"] for b in conflicts)
    verb = "is" if len(conflicts) == 1 else "are"
    print(f"\nWarning: {names} {verb} currently in your battle team.")
    print("Selling will remove them from your team.")
    confirm = input("Proceed? (y/n): ").strip().lower()
    return confirm == "y"


def cmd_sell(args: list[str]) -> None:
    if not args:
        print("Usage:")
        print("  $sell <rarity>")
        print("  $sell band <name>")
        print("  $sell all")
        return

    catalog = load_bands()
    player = get_fresh_player()
    owned = get_owned_bands(player, catalog)

    # Sell entire collection
    if args[0].lower() == "all":
        if len(args) != 1:
            print("Usage: $sell all")
            return

        if not owned:
            print("Your collection is empty.")
            return

        if not check_team_conflict(player, owned):
            print("Sale cancelled.")
            return

        sold, total = sell_bands(player, owned)
        remove_bands_from_team(player, [b["id"] for b in owned])

        save_player(player)

        print(f"Sold {sold} bands for {total} coins.")
        print(f"Coins: {player['coins']}")
        return

    # Sell a specific band
    if args[0].lower() == "band":
        if len(args) < 2:
            print("Usage: $sell band <name>")
            return

        query = " ".join(args[1:]).lower()

        match = next(
            (
                b for b in owned
                if b["name"].lower() == query
                or b["id"].lower() == query
            ),
            None,
        )

        if match is None:
            print(f"You don't own a band called '{' '.join(args[1:])}'.")
            return

        if not check_team_conflict(player, [match]):
            print("Sale cancelled.")
            return

        value = SELL_VALUES.get(match["rarity"], 10)

        remove_band(player, match["id"])
        remove_bands_from_team(player, [match["id"]])
        add_coins(player, value)
        save_player(player)

        print(f"Sold {match['name']} for {value} coins.")
        print(f"Coins: {player['coins']}")
        return

    # Sell all bands of a specific rarity
    rarities = {
        "common": "Common",
        "uncommon": "Uncommon",
        "rare": "Rare",
        "epic": "Epic",
        "legendary": "Legendary",
    }

    rarity_key = args[0].lower()

    if rarity_key in rarities:
        if len(args) != 1:
            print(f"Usage: $sell {rarity_key}")
            return

        rarity = rarities[rarity_key]
        bands = get_bands_by_rarity(player, catalog, rarity)

        if not bands:
            print(f"You don't own any {rarity} bands.")
            return

        if not check_team_conflict(player, bands):
            print("Sale cancelled.")
            return

        sold, total = sell_bands(player, bands)
        remove_bands_from_team(player, [b["id"] for b in bands])

        save_player(player)

        print(f"Sold {sold} {rarity} band(s) for {total} coins.")
        print(f"Coins: {player['coins']}")
        return

    print(f"Unknown sell option: {' '.join(args)}")
    print("Use: $sell <rarity>, $sell band <name>, or $sell all")
