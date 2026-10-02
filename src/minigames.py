import math
import select
import sys
import termios
import time
import tty

from src.config import DRUM_COOLDOWN_SECONDS, DRUM_REWARDS


def _key_available() -> bool:
    """Check whether a key has been pressed without blocking."""
    return bool(select.select([sys.stdin], [], [], 0)[0])


def _read_key() -> str:
    """Read a single keypress without requiring Enter."""
    return sys.stdin.read(1)


def can_play_drum_roll(player: dict) -> bool:
    """Return True if the player can play Drum Roll."""
    last_played = player.get("last_drum_roll", 0)
    return time.time() - last_played >= DRUM_COOLDOWN_SECONDS


def get_drum_cooldown(player: dict) -> int:
    """Return remaining Drum Roll cooldown in seconds."""
    last_played = player.get("last_drum_roll", 0)
    remaining = DRUM_COOLDOWN_SECONDS - (time.time() - last_played)
    return max(0, int(remaining))


def play_drum_roll(player: dict) -> dict | str:
    """
    Play the Drum Roll timing minigame.

    The marker moves back and forth across the bar,
    accelerating toward the center and slowing down
    after passing it. Rewards depend on the final tile.
    """
    if not can_play_drum_roll(player):
        remaining = get_drum_cooldown(player)
        return f"Drum Roll is on cooldown. Try again in {remaining}s."

    print("\n🥁 DRUM ROLL")
    print("\nHit SPACE when the marker reaches the center!")
    print()

    width = 30
    target_position = width // 2
    duration = 1.2

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)

        start = time.time()
        final_position = 0

        while True:
            elapsed = time.time() - start

            # Repeat the animation continuously.
            cycle = (elapsed / duration) % 2.0

            # 0 → 1 → 0 movement across the bar.
            if cycle <= 1.0:
                progress = cycle
            else:
                progress = 2.0 - cycle

            # Slow start → fast center → slow finish.
            position_progress = 0.5 - 0.5 * math.cos(
                progress * math.pi
            )

            position = int(position_progress * width)

            bar = ["-"] * (width + 1)
            bar[target_position] = "|"
            bar[position] = "X"

            sys.stdout.write(
                "\r[" + "".join(bar) + "]"
            )
            sys.stdout.flush()

            if _key_available():
                key = _read_key()

                if key == " ":
                    final_position = position
                    break

            time.sleep(0.01)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    print()

    distance = abs(final_position - target_position)

    if distance == 0:
        result = "perfect"
    elif distance <= 2:
        result = "great"
    elif distance <= 5:
        result = "good"
    else:
        result = "miss"

    reward = DRUM_REWARDS[result]

    player["last_drum_roll"] = time.time()

    return {
        "result": result,
        "position": final_position,
        "target": target_position,
        "distance": distance,
        "reward": reward,
    }