# metal-shell

A terminal-based collectible strategy game centered around metal bands.

Collect **139 bands across 20 subgenres**, open genre-specific packs, manage your collection and economy, and build a three-band lineup for **Last Band Standing**.

## Features

* **139 collectible bands**
* **20 metal subgenres**
* **5 rarity tiers**
* **Weighted pack system**
* **Collection & progression tracking**
* **Coin economy**
* **Duplicate auto-selling**
* **Daily rewards**
* **Passive income**
* **Three-band team system**
* **Last Band Standing battle system**

## Band Cards

Each band has six attributes used throughout the game:

```text
╔════════════════════════════════╗
║             GOJIRA             ║
║        Progressive Metal       ║
╠════════════════════════════════╣
║ Riffs          92              ║
║ Vocals         84              ║
║ Drums          90              ║
║ Heaviness      97              ║
║ Atmosphere     88              ║
╠════════════════════════════════╣
║ Rarity         ★★★★☆         ║
╚════════════════════════════════╝
```

Rarity determines **scarcity**, not combat strength.

## Commands

| Command        | Description          |
| -------------- | -------------------- |
| `$bands`       | View collection      |
| `$band <name>` | View band card       |
| `$packs`       | View available packs |
| `$open <pack>` | Open a pack          |
| `$sell <name>` | Sell a band          |
| `$coins`       | View coin balance    |
| `$team`        | View or set team     |
| `$clear`       | Clear terminal       |
| `$help`        | Show commands        |
| `$exit`        | Exit                 |

## Run

```bash
git clone https://github.com/neptunedev77/metal-shell.git
cd metal-shell

python3 -m venv metal-env
source metal-env/bin/activate

python3 -m src.main
```

---

*Developed with Python, Linux, and a lot of metal.*

