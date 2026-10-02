from src.cards import load_bands
from src.collection import (
    save_player, get_owned_bands, set_team, get_team_bands,
    add_band_to_team, remove_band_from_team,
)
from src.commands.common import get_fresh_player


def cmd_team(args: list[str]) -> None:
    catalog = load_bands()
    player = get_fresh_player()
    owned = get_owned_bands(player, catalog)

    if args and args[0].lower() == "add":
        if len(args) < 2:
            print("Usage: $team add <name>")
            return
        query = " ".join(args[1:]).lower()
        match = next(
            (b for b in owned if b["name"].lower() == query or b["id"].lower() == query),
            None,
        )
        if match is None:
            print(f"You don't own a band called '{' '.join(args[1:])}'.")
            return
        error = add_band_to_team(player, match["id"])
        if error:
            print(error)
            return
        save_player(player)
        print(f"Added {match['name']} to your team.")
        return

    if args and args[0].lower() == "remove":
        if len(args) < 2:
            print("Usage: $team remove <name>")
            return
        query = " ".join(args[1:]).lower()
        catalog_by_id = {b["id"]: b for b in catalog}
        team_ids = player.get("team", [])
        match_id = next(
            (bid for bid in team_ids if catalog_by_id.get(bid, {}).get("name", "").lower() == query
             or bid.lower() == query),
            None,
        )
        if match_id is None:
            print(f"'{' '.join(args[1:])}' is not in your team.")
            return
        remove_band_from_team(player, match_id)
        save_player(player)
        print(f"Removed {catalog_by_id[match_id]['name']} from your team.")
        return

    if not args:
        team = get_team_bands(player, catalog)
        if not team:
            print("You haven't set a team yet. Use: $team <band1>, <band2>, <band3>")
            return
        print("Current team:")
        for band in team:
            print(f"  - {band['name']} ({band['rarity']})")
        return

    raw = " ".join(args)
    names = [n.strip().lower() for n in raw.split(",")]

    if len(names) != 3:
        print("You must choose exactly 3 bands, separated by commas.")
        print("Example: $team gojira, metallica, slipknot")
        return

    if len(set(names)) != 3:
        print("You can't pick the same band twice.")
        return

    owned_by_name = {b["name"].lower(): b for b in owned}
    owned_by_id = {b["id"].lower(): b for b in owned}

    chosen = []
    for n in names:
        band = owned_by_name.get(n) or owned_by_id.get(n)
        if band is None:
            print(f"You don't own a band called '{n}'.")
            return
        chosen.append(band)

    set_team(player, [b["id"] for b in chosen])
    save_player(player)

    print("Team set:")
    for band in chosen:
        print(f"  - {band['name']} ({band['rarity']})")
    print("\nReady for battle. Use $battle to fight!")
