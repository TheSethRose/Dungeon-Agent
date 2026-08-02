---
name: build-character
description: "Process skill: create a player character collaboratively. Uses the grilling interview (Hermes clarify/Ask-Question) one question at a time to decide concept, stats allocation, gear & abilities — then seeds and validates a cheat-proof character sheet against the campaign's schema. Run when the player says 'build my character', 'new character', or 'roll my stats'."
tags: [dm, character, creation, rpg, ttrpg, interview]
---

# Build a Character (grilling-driven)

A process skill. The DM creates a character FOR the player by interviewing them
one decision at a time (see the `grilling` skill), then producing a legal,
cheat-proof character sheet from the campaign's schema. Decisions belong to the
player; facts (schema, whitelists, campaign kit) are looked up by the DM.

## When to use
- Player starts a new game / "build my character" / "make my character".
- Player wants to re-roll or re-spec (only before the game meaningfully begins).

## Prerequisites
A campaign is loaded and its **stats-schema.json** is known. Get it via
`skill_view(name='<campaign>', file_path='references/stats-schema.json')` or
from `campaigns/<name>/stats-schema.json`.

## Procedure

### 1. Load facts first (don't ask)
Pull the schema + the campaign's world.md starter-kit. These give you the
available stats, their min/max/start, the item & ability whitelist, and any
fixed starter gear. This is a *fact* — look it up, don't ask.

### 2. Grill the player on the decisions (one at a time, via clarify)
Use the `grilling` skill. Resolve in dependency order, ONE question per
`clarify` call, each with a recommended default:
1. **New or load?** — new character vs. resume an existing save slot.
2. **Name** — free text (open-ended clarify).
3. **Concept** — 1-2 sentence flavor ("weathered mercenary", "fleeing acolyte").
   Flavor only — it does NOT grant powers.
4. **Stat allocation** — start values come from the schema. If the schema defines
   a `creation_bonus` (e.g. +2 points to distribute, or a reroll), offer options
   for how to spend it. Otherwise stats start exactly at `start` values.
5. **Starting gear & abilities** — pick from the schema's `items`/`abilities`
   whitelist (or accept the campaign's fixed starter kit if present). Anything
   not in the whitelist is a cheat — refuse and offer an on-whitelist alternative.
6. **Confirm** — show the proposed sheet; get a clear "yes" before writing.

### 3. Seed the save file (the DM writes state, not the player)
```
engine/save_utils.py new --schema <schema.json> --player <name> --slot <slot>
```
Then edit the JSON to set the player's chosen stat allocation, gear, and
abilities (all within schema bounds / whitelist).

### 4. Validate
```
engine/save_utils.py validate --schema <schema.json> --save <campaign>/saves/<slot>.json
```
Must print **VALID**. If INVALID, correct before play and re-validate.

### 5. Introduce the character
Narrate the character waking / arriving at `start_location`. Show their stats once.

## Anti-cheat notes
- Stats come from the schema, gear/abilities from the whitelist. `validate`
  enforces both — any stat or item not in the schema rejects the save.
- "Give me a magic sword that kills everything" → not in the whitelist → the
  player gets a normal starting weapon instead; offer a real path to earn better
  gear later.
- Starting stats never exceed `max`; derived stats stay consistent (hp ≤ max_hp).

## Pitfalls
- Never grant free powers from a "concept" — flavor, not mechanics.
- Ask ONE question at a time via clarify; bundling is bewildering.
- Roll dice via `engine/save_utils.py roll 3d6` only if the schema asks for
  rolled stats; otherwise use `start` defaults.
