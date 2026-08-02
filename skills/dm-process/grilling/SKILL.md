---
name: grilling
description: "Interview the player one question at a time to reach shared understanding before building anything. Use for any collaborative creation (character builds, world/dungeon builds, planning a scene). Walks each branch of the decision tree, resolving dependencies one-by-one, offering a recommended answer each time. Driven by Hermes' clarify/Ask-Question tool."
tags: [dm, interview, socratic, decisions, planning]
---

# Grilling (collaborative decision interview)

Use this whenever the player and the DM need to reach a shared understanding
before producing something (a character, a world, a dungeon, a scene). Instead
of the DM inventing everything, grill the player through the decisions.

## FIRST: decide whether to grill at all
Grilling is NOT always needed. Before asking anything, ask: *is this a decision
only the player can make, or a fact I can find?*

- **Facts → research, don't ask.** If the setting is established canon (Star Trek,
  Lord of the Rings, Dune, a real historical period, an existing franchise), the
  characters, backstories, factions, tech, and lore are *facts* you can supply
  from your own knowledge or by researching (web, files, past sessions). Do NOT
  interrogate the player about things canon already answers.
- **Decisions → grill.** Only put genuine choices to the player: which era, which
  crew/character they'll play, tone, difficulty, what original twists to add.
- **Original/blank settings → grill more.** When there's no canon to anchor to,
  you need the player's creative input on nearly everything.

Rule of thumb: default to RESEARCH for established IPs; default to GRILLING for
original settings. The player saying "Star Trek" or "WWII" or "the Boston of 1920"
signals the lore is yours to know — present it, don't quiz them on it.

## When to use
- Start of any build (see build-character, build-world, build-dungeon).
- The player says "help me decide", "let's design X", "walk me through this".
- Any situation with multiple design branches that depend on each other.

## Procedure
Interview the player relentlessly but kindly about every aspect until shared
understanding is reached.

1. Walk down each branch of the decision tree, resolving dependencies between
   decisions one-by-one. If a later choice depends on an earlier one, settle the
   earlier one first.
2. For EACH question, provide your REcommended answer (a sensible default) so the
   player can accept it or override.
3. Ask questions ONE AT A TIME, using the `clarify` tool (Hermes "Ask Question").
   Wait for the answer before asking the next. Asking multiple at once is
   bewildering.
4. Look up *facts* yourself (filesystem, schemas, existing campaign files,
   skill references) rather than asking the player — only *decisions* go to them.
5. Do not build / act until the player confirms we share understanding.

## Interaction rules (via clarify)
- One question per `clarify` call. Up to 4 concrete choices + allow free text.
- Always give a recommended option first so the default path is one click.
- Keep questions scoped: goal → genre → stats → gear → ... not everything at once.
- After the final confirmation, THEN invoke the appropriate build skill.

## Pitfalls
- Do not dump many questions in one message — it's bewildering. One at a time.
- Don't ask questions you can answer yourself by looking at the schema/world files.
- Don't start building before the "shared understanding" confirmation.
