from src.collection import load_player, save_player, regen_income
from src.packs import get_remaining_packs, can_claim_daily
from src.commands import COMMANDS

PROMPT = "$ "


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
