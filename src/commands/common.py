from src.collection import load_player, save_player, regen_income


def get_fresh_player() -> dict:
    """Load the player and apply any passive income earned since last check."""
    player = load_player()
    regen_income(player)
    save_player(player)
    return player
