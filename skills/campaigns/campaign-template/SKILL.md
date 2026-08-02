---
name: campaign-template
description: "Blank template for authoring a new dungeon-crawl campaign as a skill. Copy this skill (rename with a new campaign name), fill in references/stats-schema.json (character stats for THIS game) and references/world.md (premise, locations, monsters, loot, win condition), and register it so the DM can load it. The anti-cheat code and save/load engine are inherited from AGENTS.md — you only define content."
tags: [campaign, template, rpg, ttrpg, authoring]
---

# Campaign Template

Use this to author a NEW campaign. The Dungeon Master (AGENTS.md) is generic —
it runs ANY campaign. Your job is to define this game's **content** only. The
rules engine, anti-cheat code, combat, and save/load are all inherited.

## How to make a new campaign skill
1. Copy this skill's directory and rename it `campaign-<yourname>`.
2. Edit `references/stats-schema.json`:
   - `campaign` — unique id used for the save-folder name.
   - `start_location` — where the player begins.
   - `stats` — THE CHARACTER STATS FOR THIS GAME. Each: name, type (int/float),
     min, max, start. Example: hp, max_hp, atk, def, level, xp, gold, mana.
   - `derived` — recomputed stats (e.g. max_hp grows with level). Formula in `expr`.
   - `items` / `abilities` — the ONLY items/abilities that can ever appear on a
     character sheet. Anything else is rejected by validation (anti-cheat).
   - `rooms` — optional list of room ids the world.md defines (for durable world state).
   - `win_condition` — what ends the game.
3. Edit `references/world.md` — premise, locations/exits, monsters, loot, XP curve.
4. Edit `references/persona.md` — the DM's narrator voice/tone for THIS campaign.
5. Update this SKILL.md's description + starting procedure to match.

## Schema invariants (do not break)
- Every stat the game uses must be declared. Unknown stats are treated as cheats.
- Starting values must be within min/max. Defaults: use `start`.
- `derived` targets are recomputed on every validation — keep them consistent.
- `items` and `abilities` are whitelists: a player can NEVER have anything not
  listed here. This is the backbone of the no-invented-powers rule.

## Validation
Always seed + validate a fresh save before first play:
```
engine/save_utils.py new --schema <schema.json> --player <name> --slot <slot>
engine/save_utils.py validate --schema <schema.json> --save <save.json>
```
Validate again any time you edit the schema.
