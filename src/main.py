import os

from src.cards import load_bands, format_card, format_band_list
from src.collection import load_player, save_player, get_owned_bands

PROMPT = "$ "


def cmd_help(args: list[str]) -> None:
    print("Available commands:")
    print("  $bands             - list all bands you own")
    print("  $band <name>       - show the detailed card for a band you own")
    print("  $coins             - show how many coins you have")
    print("  $clear             - clear the terminal")
    print("  $help              - show this help")
    print("  $exit              - exit the game")


def cmd_bands(args: list[str]) -> None:
    catalog = load_bands()
    player = load_player()
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
    player = load_player()
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


def cmd_coins(args: list[str]) -> None:
    player = load_player()
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
    "coins": cmd_coins,
    "clear": cmd_clear,
    "exit": cmd_exit,
}


def main():
    print("Welcome to Metal Shell. Type $help to see the available commands.")
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