"""
Central place for all balance values. Edit numbers here, nothing else.
"""

# --- Rarities -------------------------------------------------------------
# Drop chance weights when drawing a band (packs, daily, BOT team).
RARITY_WEIGHTS = {
    "Common": 50,
    "Uncommon": 25,
    "Rare": 15,
    "Epic": 7,
    "Legendary": 3,
}

# Coins received when selling a band (also used for duplicates).
SELL_VALUES = {
    "Common": 20,
    "Uncommon": 40,
    "Rare": 80,
    "Epic": 150,
    "Legendary": 300,
}

# --- Packs ----------------------------------------------------------------
PACK_COST = 300
MAX_PACKS = 5
REGEN_INTERVAL_SECONDS = 12 * 60        # 1 new pack every 12 minutes
DAILY_COOLDOWN_SECONDS = 24 * 60 * 60

# --- Passive income -------------------------------------------------------
INCOME_AMOUNT = 5                       # coins per interval
INCOME_INTERVAL_SECONDS = 60
MAX_INCOME_MINUTES = 120                # cap: at most 2 hours accumulated

# --- Battle ---------------------------------------------------------------
BATTLE_REWARD = 200

# --- Drum Roll minigame ---------------------------------------------------
DRUM_COOLDOWN_SECONDS = 60
DRUM_REWARDS = {
    "perfect": 100,
    "great": 60,
    "good": 30,
    "miss": 0,
}
