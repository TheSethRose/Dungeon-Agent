---
name: dungeon-master-engine
description: "The architecture and subsystem knowledge for the dungeon-crawl game system (a text-based TTRPG that runs on Hermes). Covers how the system is wired: AGENTS.md as a universal DM, campaigns-as-skills, schema-driven character stats, save/load with session continuity, atomic/crash-safe writes, and the schema-whitelist anti-cheat. Use when building or extending the engine itself (save_utils.py, AGENTS.md), wiring new campaigns, or reasoning about save/load and anti-cheat. Does NOT create content — that is build-world/build-character/build-dungeon/build-situation."
tags: [dm, engine, architecture, save-load, anti-cheat, rpg, ttrpg]
---

# Dungeon Master Engine (system architecture)

The reusable mental model for the text-based TTRPG running on Hermes. The
per-session PROCS (how to build a character, a world, a dungeon, a scene) live in
the sibling `build-*` and `grilling` skills. THIS skill is the subsystem model:
how the pieces are wired together, the invariants that hold, and the pitfalls
that have cost real debugging time.

## Core architecture

- **SOUL.md** (`HERMES_HOME/SOUL.md`) is the agent identity and defines TWO modes:
  - **Mode 1 — Guide (default, no campaign loaded):** help the player decide
    what to do, answer questions, help build. No roleplay.
  - **Mode 2 — Persona (campaign loaded):** adopt the campaign's narrator
    voice/tone and run in-character. Never lowers anti-cheat or save discipline.
  Which mode is active is determined by the engine's current-game pointer
  (`engine/save_utils.py current` / `.current.json`).
- **AGENTS.md** (`dungeons/AGENTS.md`) is the **universal DM** — it is
  campaign-agnostic. It defines: the turn loop (observe -> narrate -> wait ->
  resolve -> persist), the command vocabulary, save/load protocol, the anti-cheat
  code, death/restart, and durable world state. It runs ANY campaign.
- **Campaigns are skills. Each campaign is a self-contained folder:**
  ```
  skills/campaigns/<name>/
    SKILL.md                     <- loadable brief (trigger: "play <name>")
    references/stats-schema.json <- THIS game's character stats + whitelists
    references/world.md          <- premise, locations, monsters, loot, win condition
    references/persona.md        <- DM narrator voice/tone for this campaign (Mode 2)
    saves/<slot>.json            <- CHARACTER PROGRESS (lives inside the campaign)
  ```
  Campaigns do NOT get their own AGENTS.md — the universal AGENTS.md is the one
  and only project-context file (Hermes loads one project-context per session,
  first-match-wins). Campaign behavior/persona live in the campaign SKILL.md /
  world.md / persona.md, loaded via skill_view.
- **Engine CLI** = `engine/save_utils.py` (dice, combat, save/autosave, validate,
  registry, continuity, room/death state). Full command reference in
  `references/save_utils-commands.md`.

## CRITICAL INVARIANTS (learned the hard way)

1. **Saves MUST live inside the campaign folder** (`<campaign>/saves/`), never in
   a shared engine-level `saves/` dir. This is what makes a campaign portable:
   copying the whole folder carries content AND progress together. If saves live
   outside, "copy to another agent" silently loses the player's HP/inventory/location.
2. **Always validate before narrating.** `validate --schema <schema> --save <save>`
   must print VALID before you trust or resume from a save. Invalid = refuse,
   restore last good slot, or re-seed.
3. **Writes are atomic** (temp file + rename via `write_json`) so a crashed session
   leaves the last good state intact. Never hand-edit a save with a non-atomic tool.
4. **The DM is the ONLY writer of state.** The player never edits JSON. This is
   enforced by custom schema validation, not by trust.
5. **`resume`/continuity**: a `.current.json` pointer records the active
   campaign/slot + a one-line "previously on" summary. Always refresh the player
   field from the actual save file when writing the pointer (reading a stale
   pointer shows the wrong character name).

## Anti-cheat (schema-driven, non-negotiable)

The player cannot invent stats, powers, items, or wins — because the schema is
the whitelist and validation rejects anything else:
- `stats` declared in the schema; unknown stats -> `unknown_stat`.
- `items` / `abilities` arrays are strict whitelists; anything else ->
  `unknown_item` / `unknown_ability`.
- `derived` formulas (e.g. max_hp from level) recompute on every validate;
  mismatch -> `derived_mismatch` (catches sneaky stat edits).
- `rooms` whitelist -> `unknown_room`.
- Over-max / under-min -> `above_max` / `below_min`.
The DM's behavioral anti-cheat (veto, no self-award, no trivial bypass, no
meta-gaming) lives in AGENTS.md and applies on top of this mechanical enforcement.

## Research vs. grill (user preference — IMPORTANT)

Do NOT always interview the player. Split decisions vs. facts:
- **Established IP / era** (Star Trek, LOTR, Dune, 1920s Chicago) -> the lore is a
  FACT: supply it from your own knowledge / research. Do not quiz the player on canon.
- **Genuine decisions** (era, character, tone, difficulty, twists) -> grill one
  question at a time via `clarify`, offering a recommended default each.
- **Original settings** -> grill more; there's no canon to anchor to.
See the `grilling` skill for the full procedure.

## Memory discipline (USER.md / MEMORY.md)
- USER.md (memory target `user`) may hold a FEW durable, cross-game/campaign
  preferences (e.g. preferred era, tone, turn pacing). Use it rarely.
- NEVER store campaign-specific character state (stats, HP, inventory, location,
  quest flags) in memory — that lives ONLY in the campaign save file
  (`<campaign>/saves/<slot>.json`) and is portable with the campaign.
- Rule of thumb: if it's about one campaign or one character, it's game state,
  not memory. Only generalized, durable player preferences go to USER.md.

## Pitfalls

- **Portability regression**: putting saves in a shared dir breaks copy-the-campaign.
  If you move save locations, update AGENTS.md, save_utils.py, README, and the
  build-world/build-character validate examples together (they reference paths).
- **Stale continuity pointer**: always re-read the player's name from the save
  file when updating `.current.json`, don't reuse an old `player` value.
- **Broadcast example commands**: keep campaign path examples in sync across
  skills (README, build-world, build-character, play) whenever the engine layout changes.
- **Schema drift**: every item/ability/room referenced in world.md must be listed
  in the schema whitelist or validation fails loudly — keep them in sync.

## Support files
- `references/save_utils-commands.md` — full engine CLI command reference.
