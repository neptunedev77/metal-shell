from src.commands.system import cmd_help, cmd_clear, cmd_exit
from src.commands.bands import cmd_bands, cmd_band, cmd_progress, cmd_coins
from src.commands.packs import cmd_packs, cmd_open, cmd_daily
from src.commands.team import cmd_team
from src.commands.sell import cmd_sell
from src.commands.battle import cmd_battle
from src.commands.minigames import cmd_drum

COMMANDS = {
    "help": cmd_help,
    "bands": cmd_bands,
    "band": cmd_band,
    "packs": cmd_packs,
    "open": cmd_open,
    "battle": cmd_battle,
    "daily": cmd_daily,
    "sell": cmd_sell,
    "progress": cmd_progress,
    "team": cmd_team,
    "coins": cmd_coins,
    "drum": cmd_drum,
    "clear": cmd_clear,
    "exit": cmd_exit,
}
