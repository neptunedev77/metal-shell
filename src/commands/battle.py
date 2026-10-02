from src.cards import load_bands
from src.collection import save_player, add_coins, get_team_bands
from src.battle import (
    create_battle_team, alive_bands, is_team_defeated, resolve_round, draw_attribute,
)
from src.bot import generate_bot_team, choose_band as bot_choose_band
from src.commands.common import get_fresh_player

BATTLE_REWARD = 200


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
