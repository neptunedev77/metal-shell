from src.collection import save_player, add_coins
from src.minigames import play_drum_roll
from src.commands.common import get_fresh_player


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
