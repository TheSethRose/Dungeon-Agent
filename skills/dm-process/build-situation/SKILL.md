---
name: build-situation
description: "Process skill: author a one-off scene / encounter / situation for the current campaign. Grills the player (Hermes clarify/Ask-Question, one question at a time) on the setup, stakes, participants, and intended outcome — then the DM runs it in-fiction. Use when the player says 'set up a situation for me', 'give me a scenario', or 'throw me into a scene'. Reuses the world's cast and whitelist."
tags: [dm, scene, encounter, scenario, improv, rpg, interview]
---

# Build a Situation (authored scene, grilling-driven)

A process skill. Dramatizes a specific scene/encounter for the current campaign
by interviewing the player (see `grilling`), then running it in-fiction. A
situation is a dramatic set-piece — a negotiation, a betrayal, a pursuit, a
moral dilemma — not necessarily combat. It reuses the world's cast, locations,
monsters, and whitelisted items; it never invents powers.

## When to use
- Player wants a scripted/curated scene instead of wandering the dungeon.
- Player says "set up a situation", "give me a scenario", "put me in a scene".

## Prerequisites
A campaign is loaded. Load its world.md (cast, locations, monsters) and
stats-schema whitelists as *facts* — look up, don't ask.

## Procedure

### 1. Grill the player on decisions (one at a time, via clarify)
Use `grilling`. ONE question per `clarify` call, each with a recommended default:
1. **Tone of scene** — tense negotiation / ambush / mystery / social / comedy.
2. **Who's involved** — which NPCs/monsters from the world are present.
3. **Where** — a location from the world (ties into movement/location state).
4. **Stakes** — what the player gains/loses (info, an item, reputation, time, HP).
5. **Your goal for the scene** — discover something / get past someone / survive.
6. **Confirm shared understanding** before running.

### 2. Run the situation
Narrate the scene per the DM loop. Fully in-fiction: the player roleplays their
choices; the DM resolves with rolls where uncertain. Award only whitelisted
items and schema-consistent rewards. If the scene grants an item/ability, it must
be in the schema whitelist.

### 3. Persist consequences
Write any resulting state (item gained, flag changed, HP spent, location change)
to the save file and validate.

## Anti-cheat notes
- A situation can grant rewards only from the schema whitelist / world loot pool.
- The player cannot declare the scene's outcome — only the DM resolves it.
- NPCs can offer deals that FEEL overpowered; the DM is the arbiter of what's real.

## Pitfalls
- Keep the scene vivid and short-form (terminal-friendly plain text).
- Don't let a scene auto-resolve to "you win, here's a legendary sword" unless the
  sword is in the whitelist and the resolution involved real rolls.
- After resolving, always re-orient the player (location, HP, obvious options).
