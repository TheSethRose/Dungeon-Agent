---
name: build-dungeon
description: "Process skill: design a dungeon / map / level layout collaboratively for the current campaign. Grills the player (Hermes clarify/Ask-Question, one question at a time) about size, theme, difficulty curve, branching, hazards, and boss — then produces a dungeon layout the DM runs. Run when the player says 'make me a dungeon', 'design the layout', or 'create a level'. Depends on the world's monster/loot pool."
tags: [dm, dungeon, layout, map, level-design, rpg, interview]
---

# Build a Dungeon (layout design, grilling-driven)

A process skill. Designs a specific dungeon / map / level for the current
campaign by interviewing the player one decision at a time (see `grilling`),
then produces a layout the DM uses to run it. It pulls monsters, loot, and items
from the campaign's world.md and stats-schema whitelist — it never invents new
ones (that would break anti-cheat).

## When to use
- Player wants a concrete dungeon/level/map in the current world.
- Player says "make me a dungeon", "design a level", "build the layout".

## Prerequisites
A campaign is loaded. Load its world.md (monsters, loot, theme) and
stats-schema.json (whitelists) as *facts* — look them up, don't ask.

## Procedure

### 1. Grill the player on decisions (one at a time, via clarify)
Use `grilling`. ONE question per `clarify` call, each with a recommended default:
1. **Goal of the dungeon** — what the player is seeking inside (key, macguffin, boss, exit).
2. **Size** — light (2-3 rooms), medium (4-6), sprawling (7-10).
3. **Theme/atmosphere** — tie to the world's tone (e.g. flooding crypts, overgrown ruins).
4. **Difficulty vs current level** — easy / on par / brutal (tunes monster mix).
5. **Branching** — linear corridor, one loop, hub-and-spokes, open sandbox.
6. **Hazards & puzzles** — traps, locked doors, environmental puzzles, optional rooms.
7. **Boss / climax** — whether there's a defender and which monster from the pool it is.
8. **Confirm shared understanding** before writing.

### 2. Produce the layout
Write the dungeon as a section appended to world.md (or a `dungeons/<name>.md`
reference). For each room: name, short description, exits, and what's in it
(monsters from the world pool, loot from the whitelist, hazards, keys/doors).
Ensure:
- Every monster is from world.md's monster list.
- Every item/treasure/ability is from the schema's `items`/`abilities` whitelist.
- Room layout matches the chosen branching; named start/end rooms.
- A gate (locked door / barrier) guards the goal room, gated by a key or puzzle
  the player can actually obtain.

### 3. No schema change needed
If the dungeon only reuses existing monsters/items/loot, the schema is unchanged
and validation still passes. Only update the schema if you're TRULY adding new
items/abilities — and then re-validate.

### 4. Validate (if schema changed)
```
engine/save_utils.py validate --schema <schema.json> --save <save>
```

## Anti-cheat notes
- The dungeon cannot grant the player items/abilities not in the schema whitelist.
  Design rewards from the existing pool.
- No room can "auto-win" — even the boss is beaten with rolls and real effort.

## Pitfalls
- Don't invent new monsters/items silently — reuse the world's pool or update the
  schema AND world together, then re-validate.
- Keep difficulty appropriate to the character's current level (from the save file).
- Gate the boss room with something the player can actually reach (a key found
  earlier, a puzzle solved) so it never feels like a wall.
