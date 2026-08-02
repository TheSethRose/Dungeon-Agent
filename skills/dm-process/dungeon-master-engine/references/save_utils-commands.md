# save_utils.py — Engine CLI Reference

Path: `dungeons/engine/save_utils.py`. The DM invokes these to run any
campaign. Generic (works for any world type); all game meaning lives in the
campaign schema + world.md, never in the engine.

## Environment overrides
- `DUNGEON_CAMPAIGN_ROOTS` — colon-separated dirs to search for campaign folders
  (defaults: profile `skills/campaigns`, then `dungeons/campaigns`). Point at a
  ported/imported campaign dir to pick up a game elsewhere.
- `DUNGEON_CURRENT_FILE` — override location of the `.current.json` pointer.

## Commands

### Dice & combat
- `roll <spec> [spec...]` — e.g. `roll 2d6+1`, `roll 1d8`. Prints rolls + total.
- `check --stat <n> --dc <n> [--bonus <n>]` — `1d20 + stat + bonus` vs DC. Nat 20
  auto-succeeds, nat 1 auto-fails. Exit 0 success / 1 fail.
- `initiative "<name>:<bonus>" ...` — e.g. `initiative "Thorn:2" "goblin:0"`.
  Returns acting order highest-first.

### Save lifecycle
- `new --schema <path> --player <name> --slot <slot>` — seed a fresh character
  from a schema. Writes atomically and sets the current-game pointer.
- `validate --schema <path> --save <path>` — check against schema. Prints VALID or
  a list of problems (`unknown_stat`, `above_max`, `below_min`, `derived_mismatch`,
  `unknown_item`, `unknown_ability`, `unknown_room`, `missing_stat`, `non_numeric`).
- `inspect --save <path>` — pretty-print a save.
- `touch --save <path> [--note <t>] [--summary <s>]` — advance turn counter + log.
- `autosave --save <path> [--summary <s>]` — persist + bump turn + update pointer.
- `death --save <path> [--note <t>]` — increment the deaths counter.

### Registry / continuity
- `list [--campaign <id>]` — campaigns, save slots (`*` = current), current pointer.
- `current` — show the active campaign/slot/player/summary.
- `resume` — print resume info for the current game (location, HP, turns, "previously on").
- `use --campaign <id> --slot <s> [--summary <t>]` — set the current-game pointer.

### Durable world state
- `room --save <path> --room <id> [--explored] [--cleared] [--npc-name <n> --npc <disp>]`
  — update per-room state (`explored`, `cleared`, per-NPC disposition) in `save.rooms`.

## Save file shape
```json
{
  "meta":  {"campaign", "schema_version", "player", "created", "updated", "turns", "deaths"},
  "stats": {"hp","max_hp","atk","def","level","xp","gold","mana","max_mana","..."},
  "inventory": [...],
  "abilities": [...],
  "flags":     {...},
  "location":  "room_id",
  "rooms":     {"<room_id>": {"explored": bool, "cleared": bool, "npcs": {...}}},
  "log":       [...],
  "obituary":  ["previously on" summaries]
}
```

## Verified behavior (from testing)
- Atomic writes leave no `.tmp` litter; a "crashed" session keeps the last good state.
- Saves resolve from any campaign root via `DUNGEON_CAMPAIGN_ROOTS`; porting = copying
  the campaign folder and setting the env var.
- A cheated save (level>max, invented stat, non-whitelist item/ability or room) is
  caught by `validate` and reported as distinct problems — the DM refuses to load it.

## Anti-cheat validation rules (schema-driven)
- Every stat must be declared; unknown -> `unknown_stat`; out of min/max bounds flagged.
- `derived` targets recomputed on every validate; mismatch -> `derived_mismatch`.
- `items` / `abilities` / `rooms` are whitelists; anything not listed is rejected.
