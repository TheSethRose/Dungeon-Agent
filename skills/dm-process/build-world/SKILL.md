---
name: build-world
description: "Process skill: AUTHOR a brand-new campaign collaboratively. Grills the player (Hermes clarify/Ask-Question, one question at a time) to decide genre, setting, goal, stats schema (this game's character stats), and world details — then writes the schema JSON + world.md, registers it as a campaign skill, and validates it runs. Run when the player says 'create a new world/campaign/game'."
tags: [dm, worldbuilding, campaign, authoring, rpg, interview]
---

# Build a World (author a new campaign, grilling-driven)

A process skill. The DM authors a NEW, runnable campaign by interviewing the
player through the design decisions (see `grilling`), then produces the two
content artifacts: **stats-schema.json** (this game's character stats) and
**world.md** (premise, locations, monsters, loot, win condition). The rules
engine, save/load, combat, and anti-cheat are inherited from AGENTS.md — you
only define content.

## When to use
- Player asks for a brand-new world/game/dungeon not in the existing campaign skills.
- Player wants a genre/style there's no campaign for yet.

## The three artifacts to produce
1. **stats-schema.json** — character sheet definition: stats (name/type/min/max/start),
   derived formulas, item & ability whitelist, win condition.
2. **world.md** — premise, locations & exits, monsters, loot, XP curve, tone.
3. **persona.md** — the DM's narrator voice/tone for THIS campaign (adopted on
   load per SOUL.md Mode 2). Optional but recommended — without it, the DM
   narrates in a neutral default.

## Procedure

### 0. Research first for established settings (skip grilling of facts)
If the player names a known IP / era (e.g. "Star Trek", "Middle-earth", "1920s
Chicago", "Warhammer 40k"), the lore is a FACT you supply — pull characters,
backstories, factions, tech, and canon from your knowledge / past sessions / web
research. Do NOT grill the player about established canon. Summarize the relevant
lore you're anchoring to, then confirm before building. (See grilling skill:
facts → research; only decisions → grill.)

### 1. Grill the player on DECISIONS only (one at a time, via clarify)
Use `grilling`. ONE question per `clarify` call, each with a recommended default.
Resolve dependencies in order:
1. **Genre/tone** — high fantasy / grimdark / sci-fi / comedy / horror.
2. **Setting** — one-line premise ("a haunted space station", "a flooded kingdom").
3. **Goal / win condition** — what ends the game.
4. **Player power level** — starting power (affects starter stat values & early monsters).
5. **Combat or puzzle focus** — how central combat is (tunes monster XP & stat weights).
6. **Confirm shared understanding** before building.

### 2. Design the stats schema (`stats-schema.json`)
Fields the engine's validator understands:
- `campaign` (unique id → save folder), `title`, `start_location`, `schema_version`.
- `stats[]` — each: `name`, `type` (`int`|`float`), `min`, `max`, `start`.
  Typical set: hp, max_hp, atk, def, level, xp, gold, mana (adapt to genre).
- `derived[]` — auto-recomputed stats: `target` + `expr` (e.g.
  `{"target":"max_hp","expr":"20+(level-1)*4"}`).
- `items[]`, `abilities[]` — the STRICT whitelist. Validator rejects anything not
  listed. Backbone of the no-invented-powers anti-cheat.
- `win_condition`.

Design rules:
- Every stat used must be declared; unknown stats are treated as cheats.
- `start` values within `min`/`max`; derived targets recompute cleanly.
- Keep whitelists complete but tight — every item/ability in world.md must be listed.
- The campaign folder is SELF-CONTAINED: schema at `references/stats-schema.json`,
  saves at `<campaign>/saves/<slot>.json` (INSIDE the folder). Keeping saves inside
  the folder is what makes the campaign portable — copying the folder carries
  progress too. Do not place saves in a shared engine-level dir.

### 3. Write the world (`world.md`)
Structure: premise → starting gear/abilities (subset of whitelist) → locations
with exits (flow start → ... → final, final named `start_location`) → monsters
(name, hp/atk/def, XP) → loot (effects) → XP & leveling → win condition.

### 4. Register it as a campaign skill
Copy `campaign-template`, rename to `campaign-<name>`, write schema + world +
persona into its `references/` (and an optional copy under `campaigns/<name>/`
for the engine's default path). Update the SKILL.md description + starting procedure.

### 5. Validate (proof it runs)
```
engine/save_utils.py new --schema campaigns/<name>/stats-schema.json --player test --slot test
engine/save_utils.py validate --schema campaigns/<name>/stats-schema.json --save campaigns/<name>/saves/test.json
```
Must print **VALID**. Fix and re-validate, then delete the test slot.

## Anti-cheat relevance
Well-formed campaigns are cheat-proof by construction: stats, items, abilities
are schema-whitelisted and validator-enforced, so the player physically cannot
have a power or stat the world doesn't define.

## Pitfalls
- Forgetting to list an item in `items[]` that world.md references → "unknown_item".
  Keep schema and world in sync.
- Derived formula errors → "derived_mismatch". Test with a fresh save.
- Don't set `start` HP so low the player dies instantly, nor so high there's no
  tension. For a level-1 crawl, 15-25 HP is a safe default.
- Reuse this skill every time you author a world for a consistent format.
