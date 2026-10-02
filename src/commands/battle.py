import time

from src.cards import load_bands
from src.collection import save_player, add_coins, get_team_bands
from src.battle import (
    create_battle_team, alive_bands, is_team_defeated, resolve_round, draw_attribute,
)
from src.bot import generate_bot_team, choose_band as bot_choose_band
from src.config import DIFFICULTIES, DEFAULT_DIFFICULTY
from src.commands.common import get_fresh_player, prompt

REVEAL_DELAY = 0.5   # seconds of suspense before the BOT's pick is shown
RESULT_COLUMN = 48   # where the WIN/LOSS verdict starts


def _names(team: list[dict]) -> str:
    return " · ".join(b["band"]["name"] for b in team)


def _print_round(number: int, attribute: str, player_team: list[dict], bot_team: list[dict]) -> dict:
    """Print the round header and the player's 3 bands (fixed slots). Returns {key: band}."""
    title = f"ROUND {number} · {attribute.upper()}"
    if number > 1:
        title = title.ljust(26) + "BOT: " + _names(alive_bands(bot_team))
    print(f"\n{title}")

    width = max(len(b["band"]["name"]) for b in player_team) + 2
    options = {}
    for idx, bb in enumerate(player_team, start=1):
        name = bb["band"]["name"]
        if bb["alive"]:
            print(f" {idx}  {name:<{width}}{bb['band']['attributes'][attribute]}")
            options[str(idx)] = bb
        else:
            print(f" {idx}  {name:<{width}}out")
    return options


def cmd_battle(args: list[str]) -> None:
    difficulty = DEFAULT_DIFFICULTY
    if args:
        if len(args) != 1 or args[0].lower() not in DIFFICULTIES:
            print(f"Usage: $battle [{'|'.join(DIFFICULTIES)}]")
            return
        difficulty = args[0].lower()
    settings = DIFFICULTIES[difficulty]
    reward = settings["reward"]

    catalog = load_bands()
    player = get_fresh_player()
    team_bands = get_team_bands(player, catalog)

    if len(team_bands) != 3:
        print("You need a full team of 3 bands first. Use: $team <a>, <b>, <c>")
        return

    player_team = create_battle_team(team_bands)
    bot_team = create_battle_team(
        generate_bot_team(catalog, settings["team_candidates"], settings["team_pick"])
    )

    print(f"\n{difficulty.upper()} · win +{reward}")
    print(_names(player_team))
    print("  vs")
    print(_names(bot_team))

    round_number = 1
    player_wins = bot_wins = 0

    while True:
        attribute = draw_attribute()
        options = _print_round(round_number, attribute, player_team, bot_team)

        choice = prompt("> ").strip()
        while choice not in options:
            keys = list(options)
            valid = keys[0] if len(keys) == 1 else ", ".join(keys[:-1]) + " or " + keys[-1]
            print(f"   Choose {valid}")
            choice = prompt("> ").strip()

        player_pick = options[choice]
        bot_pick = bot_choose_band(alive_bands(bot_team), attribute, settings["smart_chance"])

        p_name = player_pick["band"]["name"]
        b_name = bot_pick["band"]["name"]
        p_value = player_pick["band"]["attributes"][attribute]
        b_value = bot_pick["band"]["attributes"][attribute]

        # Short suspense: show our pick, then reveal the BOT's on the same line.
        print(f"   {p_name} {p_value}  vs  ", end="", flush=True)
        time.sleep(REVEAL_DELAY)

        outcome = resolve_round(player_pick, bot_pick, attribute)
        tie = " (tie)" if p_value == b_value else ""
        if outcome["winner_is_player"]:
            player_wins += 1
            verdict = f"✔ WIN{tie}"
        else:
            bot_wins += 1
            verdict = f"✘ LOSS{tie} · {p_name} is out"

        revealed = f"{b_value} {b_name}"
        left_length = len(f"   {p_name} {p_value}  vs  ") + len(revealed)
        print(revealed + " " * max(2, RESULT_COLUMN - left_length) + verdict)

        round_number += 1
        if is_team_defeated(player_team) or is_team_defeated(bot_team):
            break

    score = f"{player_wins}–{bot_wins}"
    print()
    if is_team_defeated(bot_team):
        add_coins(player, reward)
        save_player(player)
        print(f"YOU WIN  {score}  ·  +{reward} coins  ·  Coins: {player['coins']}")
    else:
        print(f"YOU LOSE  {score}")
