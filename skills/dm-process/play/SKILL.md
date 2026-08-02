---
name: play
description: "The game launcher / entry point. Boots the dungeon-crawl system, picks (or confirms) the campaign, resumes the current save or starts a new character, validates, and begins narration. This is what actually starts a session — run whenever the player says 'play', 'start the game', 'resume my game', 'new game', or names a campaign. Delegates character build, world build, dungeon build, and scenes to the build-* skills."
tags: [dm, launcher, session, rpg, ttrpg, boot]
---

# Play (game launcher)

The single entry point for the game system. This skill conducts the boot
sequence so the DM can start any campaign, resume any save, and get narrating.
Everything else (character/world/dungeon/scene building) is delegated to the
build-* skills.

## When to use
- Player says: "play", "start the game", "resume my game", "new game",
  "load my save", or names a campaign ("let's do Star Trek").
- Any time a session should begin or resume.

## Boot procedure

### 1. Orient from the saved engine state (facts, don't ask)
Run the engine to see where things stand:
```
engine/save_utils.py list
```
This reports on-disk campaigns, all save slots (marking the current one with *),
and the current-game pointer with its "previously on" summary. Use it to know
what exists BEFORE asking the player anything.

### 2. Decide: resume vs new (one genuine decision)
- If a current game exists AND the player wants to continue →
  **resume** (step 3). No need to grill.
- If the player wants a new game / new campaign →
  **start fresh** (step 4).
- If a campaign/original setting is named, first consult the grilling skill's
  research-vs-grill rule: established IP → supply canon yourself; original →
  grill the decisions.

### 3. Resume an existing game
```
engine/save_utils.py resume
```
Reads the current pointer: campaign/slot, location, HP, turns, and "previously
on". Validate the save, then re-orient the player and continue narration from
where they left off. Show location, current stats, and obvious options.

### 4. Start fresh (new campaign or new character)
- If creating/resuming a character in an EXISTING campaign, hand off to
  `build-character` (which seeds + validates the save and sets the current pointer).
- If there is NO campaign yet, hand off to `build-world` first to author one,
  then `build-character`.

### 5. Always validate before narrating
```
engine/save_utils.py validate --schema <schema> --save <save>
```
An INVALID save is refused (anti-cheat) and restored from the last good slot or
re-seeded. Never narrate from an invalid state.

### 6. Adopt the campaign persona
Before narrating, load the campaign's persona so the DM voice matches the world:
`skill_view(name='campaign-<name>', file_path='references/persona.md')` (or
`world.md` if no persona.md). Adopt that narrator voice/tone per SOUL.md Mode 2.
If no `persona.md` exists, narrate in a neutral default. Adopting a persona never
lowers the anti-cheat bar or skips save discipline.

### 7. Begin the loop
Once oriented and in persona, run the DM turn loop (observe -> narrate -> wait ->
resolve -> persist) per AGENTS.md.

## Dual-mode behavior
- If a campaign is loaded → you are in Mode 2 (persona). Narrate in-character.
- If NO campaign is loaded → you are in Mode 1 (guide). Ask what the player wants
  to do, answer questions about campaigns, or help build one. Do NOT roleplay.

## Save discipline
- Autosave after every material state change:
  `engine/save_utils.py autosave --save <save> --summary "<one-line where-we-are>"`
  The `--summary` becomes the "previously on" for the next resume — keep it
  short and current-state-focused.
- Use `touch` between beats to advance the turn counter.

## Pitfalls
- Don't ask the player questions you can answer from `list`/`resume`.
- Don't start narrating before the save is validated.
- If campaign files are missing from the skills dir, the DM must author one via
  build-world before play can begin.
