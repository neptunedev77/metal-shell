try:
    import readline
except ImportError:  # e.g. Windows without pyreadline
    readline = None

from src.collection import load_player, save_player, regen_income


def get_fresh_player() -> dict:
    """Load the player and apply any passive income earned since last check."""
    player = load_player()
    regen_income(player)
    save_player(player)
    return player


def prompt(text: str = "") -> str:
    """
    input() for menus, confirmations and battle picks. Same as input(), but the
    answer is not kept in the command history, so pressing UP at the main prompt
    gives back the last *command* (e.g. "battle") and not a stray "1" or "y".
    """
    value = input(text)
    if readline is not None and value:
        length = readline.get_current_history_length()
        if length:
            readline.remove_history_item(length - 1)
    return value
