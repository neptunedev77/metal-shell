import random

ATTRIBUTES = ["riffs", "vocals", "drums", "heaviness", "atmosphere"]


def create_battle_team(bands: list[dict]) -> list[dict]:
    """Wrap bands in battle state: alive flag only, no HP needed."""
    return [{"band": band, "alive": True} for band in bands]


def alive_bands(team: list[dict]) -> list[dict]:
    return [b for b in team if b["alive"]]


def is_team_defeated(team: list[dict]) -> bool:
    return len(alive_bands(team)) == 0


def draw_attribute() -> str:
    return random.choice(ATTRIBUTES)


def resolve_round(player_pick: dict, bot_pick: dict, attribute: str) -> dict:
    """
    Compare the chosen bands on the given attribute. The loser is
    eliminated instantly; the winner takes no damage.
    """
    player_value = player_pick["band"]["attributes"][attribute]
    bot_value = bot_pick["band"]["attributes"][attribute]

    if player_value == bot_value:
        winner_is_player = random.choice([True, False])
    else:
        winner_is_player = player_value > bot_value

    loser = bot_pick if winner_is_player else player_pick
    loser["alive"] = False

    return {
        "player_value": player_value,
        "bot_value": bot_value,
        "winner_is_player": winner_is_player,
        "loser": loser,
    }