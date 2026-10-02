import time

from src.cards import load_bands
from src.collection import save_player, has_rarity
from src.packs import (
    PACKS, open_pack, get_remaining_packs, get_seconds_until_next_pack,
    format_countdown, claim_daily, can_claim_daily, get_pool_hint,
)
from src.config import MAX_PACKS
from src.commands.common import get_fresh_player


def dramatic_pause(label: str) -> None:
    print(f"\n{label}", end="", flush=True)
    for _ in range(3):
        time.sleep(0.3)
        print(".", end="", flush=True)
    print()


def print_milestone_banner(text: str) -> None:
    bar = "━" * len(text)
    print(f"\n{bar}")
    print(text)
    print(f"{bar}\n")


def announce_result(band: dict, is_new: bool, had_before: dict) -> None:
    """Print the drawn band, with NEW tag and rarity milestone if applicable."""
    tag = " ✨ NEW!" if is_new else ""
    print(f"\n{band['name'].upper()} ({band['rarity']}){tag}")

    rarity = band["rarity"]
    if rarity in ("Legendary", "Epic") and not had_before.get(rarity, True):
        print_milestone_banner(f"FIRST {rarity.upper()} OF YOUR COLLECTION!")
    elif rarity == "Rare" and not had_before.get(rarity, True):
        print("Nice pull! That's your first Rare in your collection.")


def cmd_packs(args: list[str]) -> None:
    catalog = load_bands()
    player = get_fresh_player()
    remaining = get_remaining_packs(player)

    print(f"Packs available: {remaining}/{MAX_PACKS}")
    if remaining < MAX_PACKS:
        wait = format_countdown(get_seconds_until_next_pack(player))
        print(f"Next pack in: {wait}")

    hint = get_pool_hint(player, catalog)
    if hint:
        print(f"Pool hint: {hint} hasn't given you a Legendary yet...")

    print()
    print("Pack types:")
    print(f"  {'Type':<24}{'Name':<28}{'Cost':<10}")
    for pack_type, pack in PACKS.items():
        print(f"  {pack_type:<24}{pack['display_name']:<28}{pack['cost']} coins")
    print()
    print("Use: $open <type>")


def cmd_open(args: list[str]) -> None:
    if not args:
        print("Usage: $open <pack type>")
        print("Type $packs to see the available pack types.")
        return

    pack_type = args[0].lower()
    catalog = load_bands()
    player = get_fresh_player()

    had_before = {
        "Legendary": has_rarity(player, catalog, "Legendary"),
        "Epic": has_rarity(player, catalog, "Epic"),
        "Rare": has_rarity(player, catalog, "Rare"),
    }

    pack_name = PACKS.get(pack_type, {}).get("display_name", pack_type)
    dramatic_pause(f"🥁 Opening {pack_name}...")

    result = open_pack(pack_type, player)

    if isinstance(result, str):
        print(result)
        return

    save_player(player)

    band = result["band"]
    is_new = result["is_new"]
    duplicate_value = result["duplicate_value"]

    if is_new:
        announce_result(band, True, had_before)
    else:
        print(f"\n{band['name'].upper()} ({band['rarity']}) — DUPLICATE")
        print(f"Sold for {duplicate_value} coins.")

    print(f"Coins: {player['coins']} | Packs: {get_remaining_packs(player)}/{MAX_PACKS}")


def cmd_daily(args: list[str]) -> None:
    catalog = load_bands()
    player = get_fresh_player()

    if not can_claim_daily(player):
        result = claim_daily(player)
        print(result)
        return

    had_before = {
        "Legendary": has_rarity(player, catalog, "Legendary"),
        "Epic": has_rarity(player, catalog, "Epic"),
        "Rare": has_rarity(player, catalog, "Rare"),
    }

    dramatic_pause("🎁 Claiming daily pack...")
    result = claim_daily(player)

    if isinstance(result, str):
        print(result)
        return

    save_player(player)

    if result["is_new"]:
        announce_result(result["band"], True, had_before)
    else:
        print(
            f"\n{result['band']['name'].upper()} "
            f"({result['band']['rarity']}) — DUPLICATE"
        )
        print(f"Sold for {result['duplicate_value']} coins.")

    print(f"Coins: {player['coins']}")
