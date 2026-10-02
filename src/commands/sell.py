from src.cards import load_bands
from src.collection import (
    save_player, get_owned_bands, sell_bands, get_bands_by_rarity,
    remove_bands_from_team,
)
from src.config import SELL_VALUES
from src.commands.common import get_fresh_player, prompt

USAGE = (
    "Usage:\n"
    "  $sell <band>            (several: $sell <band>, <band>)\n"
    "  $sell rarity <rarity>\n"
    "  $sell all"
)


def _plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def _total(bands: list[dict]) -> int:
    return sum(SELL_VALUES.get(b["rarity"], 10) for b in bands)


def confirm_sale(player: dict, bands: list[dict], summary: str | None = None) -> bool:
    """
    Ask for confirmation when needed. Returns True if the sale should proceed.
    - With a summary (bulk sale): always ask, showing what is about to be sold.
    - Without one: only ask if a band from the battle team is about to be sold.
    """
    team_ids = set(player.get("team", []))
    conflicts = [b for b in bands if b["id"] in team_ids]
    if summary is None and not conflicts:
        return True

    print()
    if summary:
        print(summary)
    if conflicts:
        names = ", ".join(b["name"] for b in conflicts)
        verb = "is" if len(conflicts) == 1 else "are"
        print(f"Warning: {names} {verb} in your battle team and will be removed from it.")
    return prompt("Proceed? (y/n): ").strip().lower() == "y"


def _sell(player: dict, bands: list[dict], what: str) -> None:
    sold, total = sell_bands(player, bands)
    remove_bands_from_team(player, [b["id"] for b in bands])
    save_player(player)
    print(f"Sold {what} for {total} coins.")
    print(f"Coins: {player['coins']}")


def cmd_sell(args: list[str]) -> None:
    if not args:
        print(USAGE)
        return

    catalog = load_bands()
    player = get_fresh_player()
    owned = get_owned_bands(player, catalog)
    rarities = {r.lower(): r for r in SELL_VALUES}
    first = args[0].lower()

    # $sell all
    if first == "all":
        if len(args) != 1:
            print(USAGE)
            return
        if not owned:
            print("Your collection is empty.")
            return
        summary = f"Sell all {_plural(len(owned), 'band')} for {_total(owned)} coins?"
        if not confirm_sale(player, owned, summary):
            print("Sale cancelled.")
            return
        _sell(player, owned, _plural(len(owned), "band"))
        return

    # $sell rarity <rarity>
    if first == "rarity":
        if len(args) != 2:
            print(USAGE)
            return
        rarity = rarities.get(args[1].lower())
        if rarity is None:
            print(f"Unknown rarity '{args[1]}'. Use: {', '.join(rarities)}.")
            return
        bands = get_bands_by_rarity(player, catalog, rarity)
        if not bands:
            print(f"You don't own any {rarity} bands.")
            return
        summary = f"Sell {_plural(len(bands), rarity + ' band')} for {_total(bands)} coins?"
        if not confirm_sale(player, bands, summary):
            print("Sale cancelled.")
            return
        _sell(player, bands, _plural(len(bands), rarity + " band"))
        return

    # $sell <band>[, <band>...]
    queries = [q.strip() for q in " ".join(args).split(",") if q.strip()]
    if not queries:
        print(USAGE)
        return

    lookup = {}
    for b in owned:
        lookup[b["name"].lower()] = b
        lookup[b["id"].lower()] = b

    chosen = []
    for q in queries:
        band = lookup.get(q.lower())
        if band is None:
            print(f"You don't own a band called '{q}'.")
            if q.lower() in rarities:
                print(f"Did you mean: $sell rarity {q.lower()}?")
            return
        if band not in chosen:
            chosen.append(band)

    if not confirm_sale(player, chosen):
        print("Sale cancelled.")
        return
    _sell(player, chosen, ", ".join(b["name"] for b in chosen))
