import os
import time

from src.cards import load_bands, format_card, format_band_list
from src.collection import (
    load_player, save_player, get_owned_bands, add_coins, remove_band,
    SELL_VALUES, regen_income, has_rarity, set_team, get_team_bands,
    sell_bands, get_bands_by_rarity,
)
from src.packs import (
    PACKS, open_pack, get_remaining_packs, get_seconds_until_next_pack,
    format_countdown, claim_daily, can_claim_daily, get_pool_hint,
)
from src.minigames import play_drum_roll

from src.battle import create_battle_team, alive_bands, is_team_defeated, resolve_round, draw_attribute
from src.bot import generate_bot_team, choose_band as bot_choose_band

PROMPT = "$ "
BATTLE_REWARD = 200

def get_fresh_player() -> dict:
    """Load the player and apply any passive income earned since last check."""
    player = load_player()
    regen_income(player)
    save_player(player)
    return player


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


def cmd_help(args: list[str]) -> None:
    print("Available commands:")
    print("  $bands                 - list all bands you own, grouped by genre")
    print("  $band <name>           - show the detailed card for a band you own")
    print("  $packs                 - list pack types, cost, and packs available")
    print("  $open <pack type>      - buy and open a pack")
    print("  $daily                 - claim your free daily band")
    print("  $battle                - fight a BOT using your team")
    print("  $progress              - show collection progress")
    print("  $sell <rarity>         - sell all bands of a rarity")
    print("  $sell band <name>      - sell a specific band")
    print("  $sell all              - sell your entire collection")
    print("  $team                  - view your current battle team")
    print("  $team <a>, <b>, <c>    - set your battle team")
    print("  $coins                 - show how many coins you have")
    print("  $drum                  - play Drum Roll for quick coins")
    print("  $clear                 - clear the terminal")
    print("  $help                  - show this help")
    print("  $exit                  - exit the game")


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


def cmd_packs(args: list[str]) -> None:
    catalog = load_bands()
    player = get_fresh_player()
    remaining = get_remaining_packs(player)

    print(f"Packs available: {remaining}/5")
    if remaining < 5:
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

    print(f"Coins: {player['coins']} | Packs: {get_remaining_packs(player)}/5")

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

        sold, total = sell_bands(player, owned)

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

        value = SELL_VALUES.get(match["rarity"], 10)

        remove_band(player, match["id"])
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

        sold, total = sell_bands(player, bands)

        save_player(player)

        print(f"Sold {sold} {rarity} band(s) for {total} coins.")
        print(f"Coins: {player['coins']}")
        return

    print(f"Unknown sell option: {' '.join(args)}")
    print("Use: $sell <rarity>, $sell band <name>, or $sell all")

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

def cmd_team(args: list[str]) -> None:
    catalog = load_bands()
    player = get_fresh_player()
    owned = get_owned_bands(player, catalog)

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
    print("\nReady for battle. (Battle system coming soon.)")

def cmd_drum(args: list[str]) -> None:
    player = get_fresh_player()

    result = play_drum_roll(player)

    if isinstance(result, str):
        print(result)
        return

    reward = result["reward"]
    outcome = result["result"]

    add_coins(player, reward)
    save_player(player)

    print()

    if outcome == "perfect":
        print("🔥 PERFECT!")
        print(f"+{reward} coins")

    elif outcome == "great":
        print("🥁 GREAT HIT!")
        print(f"+{reward} coins")

    elif outcome == "good":
        print("🤘 GOOD HIT!")
        print(f"+{reward} coins")

    else:
        print("💀 MISSED!")
        print("+0 coins")

    print(f"Coins: {player['coins']}")

def cmd_battle(args: list[str]) -> None:
    catalog = load_bands()
    player = get_fresh_player()
    team_bands = get_team_bands(player, catalog)

    if len(team_bands) != 3:
        print("You need a full team of 3 bands first. Use: $team <a>, <b>, <c>")
        return

    player_team = create_battle_team(team_bands)
    bot_team_bands = generate_bot_team(catalog)
    bot_team = create_battle_team(bot_team_bands)

    print("\nYOUR TEAM          BOT TEAM")
    for p, b in zip(player_team, bot_team):
        print(f"  {p['band']['name']:<18} {b['band']['name']}")
    input("\nPress Enter to begin...")

    round_number = 1
    while not is_team_defeated(player_team) and not is_team_defeated(bot_team):
        print(f"\n── ROUND {round_number} ──")
        attribute = draw_attribute()
        print(f"Attribute: {attribute.upper()}")

        alive_player = alive_bands(player_team)
        alive_bot = alive_bands(bot_team)

        if round_number > 1:
            remaining_names = ", ".join(b["band"]["name"] for b in alive_bot)
            print(f"(BOT remaining: {remaining_names})")

        print()
        options = {}
        for bb in player_team:
            if not bb["alive"]:
                continue
            idx = player_team.index(bb) + 1
            value = bb["band"]["attributes"][attribute]
            print(f"{idx}. {bb['band']['name']:<20} {value}")
            options[str(idx)] = bb

        choice = None
        while choice not in options:
            choice = input(f"\nChoose your band ({'/'.join(options.keys())}): ").strip()

        player_pick = options[choice]
        bot_pick = bot_choose_band(alive_bot, attribute)

        print(f"\nYou chose {player_pick['band']['name']} ({player_pick['band']['attributes'][attribute]})")
        print(f"BOT chose {bot_pick['band']['name']} ({bot_pick['band']['attributes'][attribute]})")
        print()

        outcome = resolve_round(player_pick, bot_pick, attribute)
        loser = outcome["loser"]
        winner_name = (
            player_pick["band"]["name"] if outcome["winner_is_player"]
            else bot_pick["band"]["name"]
        )

        print(f"{winner_name} wins! {loser['band']['name']} is ELIMINATED.")

        round_number += 1

        if is_team_defeated(player_team) or is_team_defeated(bot_team):
            break

        input("\nPress Enter to continue...")

    print()
    if is_team_defeated(bot_team):
        print("YOU WIN!")
        add_coins(player, BATTLE_REWARD)
        save_player(player)
        print(f"\n+{BATTLE_REWARD} coins")
        print(f"Coins: {player['coins']}")
    else:
        print("YOU LOSE!")
        print("Better luck next time.")

def cmd_coins(args: list[str]) -> None:
    player = get_fresh_player()
    print(f"Coins: {player['coins']}")


def cmd_clear(args: list[str]) -> None:
    os.system("clear")


def cmd_exit(args: list[str]) -> None:
    print("See you next time!")
    raise SystemExit


COMMANDS = {
    "help": cmd_help,
    "bands": cmd_bands,
    "band": cmd_band,
    "packs": cmd_packs,
    "open": cmd_open,
    "battle": cmd_battle,
    "daily": cmd_daily,
    "sell": cmd_sell,
    "progress": cmd_progress,
    "team": cmd_team,
    "coins": cmd_coins,
    "drum": cmd_drum,
    "clear": cmd_clear,
    "exit": cmd_exit,
}


def main():
    print("Welcome back, headbanger.")

    player = load_player()
    earned = regen_income(player)
    save_player(player)
    if earned:
        print(f"(+{earned} coins earned while you were away)")

    remaining_packs = get_remaining_packs(player)
    print(f"Packs ready to open: {remaining_packs}/5")

    if can_claim_daily(player):
        print("Your daily pack is ready to claim.")

    print(f"Coins: {player['coins']}")
    print("Type $help to see the available commands.")

    while True:
        try:
            raw = input(PROMPT).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not raw:
            continue

        if raw.startswith("$"):
            raw = raw[1:]

        parts = raw.split()
        command, args = parts[0].lower(), parts[1:]

        handler = COMMANDS.get(command)
        if handler is None:
            print(f"Unknown command: {command}. Type $help to see the available commands.")
            continue

        try:
            handler(args)
        except SystemExit:
            break


if __name__ == "__main__":
    main()