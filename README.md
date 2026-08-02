# Dungeon-Agent

An interactive, text-based **dungeon-crawl campaign game engine** that runs on
[Hermes Agent](https://hermes-agent.nousresearch.com). Install it as a profile
distribution and you get a universal Dungeon Master that runs any dungeon-crawl
campaign you load.

## What this agent is

- **AGENTS.md is the Dungeon Master** — a universal, campaign-agnostic engine
  (turn loop, combat, save/load, death, durable world state, anti-cheat) that
  runs ANY campaign.
- **Campaigns are installable skills.** Each campaign is a self-contained folder
  (stats schema + world + persona), so a world can be shared/ported independently.
- **Save/load with session continuity.** Game state persists; you can resume
  where you left off, and progress travels with the campaign folder.
- **Deterministic combat + schema-whitelist anti-cheat.** No invented powers,
  no self-awarded stats, no instant wins — enforced mechanically by validation.
- **Dual-mode:** when no campaign is loaded the agent acts as a helpful
  **guide** (asks what you want via selectable `clarify` buttons, answers
  questions, helps build); once a campaign is loaded it **adopts that campaign's
  persona/voice/tone**.

## Install

```bash
hermes profile install github.com/TheSethRose/Dungeon-Agent --alias
```

Then copy `.env.EXAMPLE` to `.env` and add your model provider key
(e.g. `OPENROUTER_API_KEY`), or export it in your shell.

```bash
dungeon-agent chat        # start a session
```

## Getting started

- Say **"play"** or **"start a new game"** to launch — the agent will guide you.
- Say "create a new world" / "build a character" / "make a dungeon" /
  "set up a situation" to author content (it interviews you one question at
  a time via the `clarify` tool for genuine decisions, and researches canon for
  established IPs).
- `campaign-template` ships as a blank campaign + sample schema/world to copy.

## Project layout (what ships)

```
SOUL.md                    <- personality + dual-mode (guide vs persona)
config.yaml                <- model defaults
distribution.yaml          <- install manifest
dungeons/                  <- the game engine
  AGENTS.md                <- universal Dungeon Master
  engine/save_utils.py     <- dice, combat, save/load, validate, continuity CLI
  README.md                <- engine docs
skills/
  campaigns/campaign-template/   <- blank campaign to copy for new games
  dm-process/                     <- play, grilling, build-world/character/dungeon/situation
  dm-process/dungeon-master-engine/ <- system architecture + CLI reference
```

## Excluded from this repo

Credentials (`.env`, `auth.json`), memories, sessions, logs, and all saved-game
progress are **not** shipped. Installers bring their own API keys; game saves
stay with the individual campaign folders on the player's machine.

## License

MIT
