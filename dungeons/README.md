# Dungeon Crawler — Campaign Game Engine

A text-based MMORPG-style dungeon crawl where **AGENTS.md is the Dungeon Master**
and **campaigns are skills**. The DM engine is generic — it runs any campaign
fairly, with save/load games, session-to-session continuity, and enforceable
anti-cheat rules.

## Layout
```
dungeons/
  AGENTS.md          <- The Dungeon Master (universal; works for any game)
  engine/
    save_utils.py    <- dice, combat helpers, save/autosave, validation,
                        registry, continuity pointer, room/death state (CLI)
  saves/             <- only the .current.json continuity pointer; game saves
                        live INSIDE each campaign folder
  campaigns/         <- optional content copies of campaign folders
```

## Campaigns are self-contained and portable
Each campaign is ONE folder (dropped in `skills/campaigns/<name>/`) containing
its content AND its progress:
```
skills/campaigns/<name>/
  SKILL.md                     <- campaign brief (loadable skill)
  references/stats-schema.json <- this game's character stats + whitelists
  references/world.md          <- premise, locations, monsters, loot, win condition
  saves/<slot>.json            <- CHARACTER PROGRESS (hp, inventory, location...)
```
Because the save files live inside the campaign folder, **copying the folder to
another agent carries the whole game — content and progress together.** Pointing
the engine at a ported/imported folder is a one-liner:
```
export DUNGEON_CAMPAIGN_ROOTS=/path/to/campaigns   # colon-separated
```
The engine searches these roots (defaults: profile `skills/campaigns`, then
`dungeons/campaigns`) for each campaign's schema and save folder.

## Where campaigns live (as skills)
Campaigns are Hermes **skills** under the profile:
`skills/campaigns/<name>/SKILL.md` + `references/stats-schema.json` + `references/world.md`
+ `references/persona.md` (DM voice/tone). They are pure content — the rules
engine, anti-cheat, combat, and save/load are inherited from AGENTS.md.

Campaigns do NOT get their own AGENTS.md. The single universal AGENTS.md is the
DM engine (Hermes loads one project-context per session); campaign persona and
rules live in the campaign skill files instead.

## Two modes (SOUL.md)
- **Guide** (no campaign loaded): helpful operator — ask what they want, answer
  questions, help build worlds. No roleplay. Present menu options / choices via
  the `clarify` tool (up to 4 selectable choices + free text) so the player can
  tap one.
- **Persona** (campaign loaded): adopt the campaign's narrator voice/tone from
  `persona.md` / `world.md` and run in-character. Anti-cheat + save discipline
  always stay intact.
Mode is determined by the engine current-game pointer (`engine/save_utils.py current`).

## Process skills (how the DM runs/builds on demand)
- `skills/dm-process/play` — the launcher / single entry point (boot, resume, start).
- `skills/dm-process/grilling` — research-vs-grill decision interview (one clarify
  question at a time). Established IP → DM researches canon; original → grill.
- `build-character` — create/roll a character within a campaign's schema.
- `build-world` — author a brand-new campaign (schema + world) and register it.
- `build-dungeon` — design a dungeon/level layout from the world's monster/loot pool.
- `build-situation` — author a one-off scene/encounter.
- `skills/campaigns/campaign-template` — blank campaign + sample schema/world to copy.

## Core commands (in-game)
look · go <place> · inventory · stats · take/use/equip <item> · cast <ability> ·
attack <target> · save [slot] · load [slot] · help — plus free-form roleplay.

## Save / load / continuity
- Saves: `<campaign>/saves/<slot>.json` (inside the campaign folder — travels with it).
- `.current.json` (in `dungeons/saves/`) remembers the active game + "previously on"
  summary, so `resume` picks up where you left off.
- The DM writes state atomically (crash-safe) and autosaves after each change.
- New:    `engine/save_utils.py new --schema <schema> --player <n> --slot <s>`
- Resume: `engine/save_utils.py resume`
- List:   `engine/save_utils.py list`
- Validate: `engine/save_utils.py validate --schema <schema> --save <save>`

## Combat helpers (deterministic, DM-narrated)
- Initiative: `initiative "<name>:<bonus>" ...`
- Skill/attack check: `check --stat <atk> --dc <target>`
- Damage: `roll <dice>`  (e.g. `roll 1d8+2`)

## Anti-cheat (non-negotiable, in AGENTS.md)
1. Absolute DM veto. 2. No invented abilities/items (schema whitelist).
3. No self-awarded rewards. 4. No instant-win / trivial bypass. 5. No meta-gaming
   the save. 6. Rules-as-written; DM ruling final. 7. Firm but fair.

`engine/save_utils.py validate` enforces the hard parts mechanically: unknown
stats, over-max values, derived-stat mismatches, non-whitelisted items/abilities,
and unknown rooms are all rejected.

```
# example
engine/save_utils.py roll 2d6
engine/save_utils.py new       --schema campaigns/my-campaign/stats-schema.json --player Thorn --slot main
engine/save_utils.py validate  --schema campaigns/my-campaign/stats-schema.json --save saves/my-campaign/main.json
engine/save_utils.py autosave  --save saves/my-campaign/main.json --summary "Cleared the guard room; holding a rusty key."
engine/save_utils.py resume
```
