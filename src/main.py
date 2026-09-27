from src.cards import load_bands, format_card, format_band_list
from src.collection import load_player, save_player, get_owned_bands

PROMPT = "$ "


def cmd_help(args: list[str]) -> None:
    print("Comandos disponiveis:")
    print("  $bands             - lista as bandas que possuis")
    print("  $bands <nome>      - mostra a carta detalhada dessa banda")
    print("  $coins             - mostra quantos coins tens")
    print("  $help              - mostra esta ajuda")
    print("  $exit              - sai do jogo")


def cmd_bands(args: list[str]) -> None:
    catalog = load_bands()
    player = load_player()
    owned = get_owned_bands(player, catalog)

    if not args:
        if not owned:
            print("A tua coleccao esta vazia. Ainda nao tens nenhuma banda.")
        else:
            print(format_band_list(owned))
        return

    query = " ".join(args).lower()
    match = next(
        (b for b in owned if b["name"].lower() == query or b["id"].lower() == query),
        None,
    )
    if match is None:
        print(f"Nao possuis nenhuma banda chamada '{' '.join(args)}'.")
        return
    print(format_card(match))


def cmd_coins(args: list[str]) -> None:
    player = load_player()
    print(f"Coins: {player['coins']}")


def cmd_exit(args: list[str]) -> None:
    print("Ate a proxima!")
    raise SystemExit


COMMANDS = {
    "help": cmd_help,
    "bands": cmd_bands,
    "coins": cmd_coins,
    "exit": cmd_exit,
}


def main():
    print("Bem-vindo ao Metal Shell. Escreve $help para ver os comandos.")
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
            print(f"Comando desconhecido: {command}. Escreve $help para ver os comandos.")
            continue

        try:
            handler(args)
        except SystemExit:
            break


if __name__ == "__main__":
    main()