import os


def cmd_help(args: list[str]) -> None:
    print("Available commands:")
    print("  $bands                 - list all bands you own, grouped by genre")
    print("  $band <name>           - show the detailed card for a band you own")
    print("  $packs                 - list pack types, cost, and packs available")
    print("  $open <pack type>      - buy and open a pack")
    print("  $daily                 - claim your free daily band")
    print("  $battle [difficulty]   - fight a BOT: easy, normal (default) or hard")
    print("  $progress              - show collection progress")
    print("  $sell <band>           - sell a band (several: $sell <a>, <b>)")
    print("  $sell rarity <rarity>  - sell all bands of a rarity")
    print("  $sell all              - sell your entire collection")
    print("  $team                  - view/add/remove bands (add <name>, remove <name>)")
    print("  $team <a>, <b>, <c>    - replace your whole team")
    print("  $coins                 - show how many coins you have")
    print("  $drum                  - play Drum Roll for quick coins")
    print("  $clear                 - clear the terminal")
    print("  $help                  - show this help")
    print("  $exit                  - exit the game")


def cmd_clear(args: list[str]) -> None:
    os.system("clear")


def cmd_exit(args: list[str]) -> None:
    print("See you next time!")
    raise SystemExit
