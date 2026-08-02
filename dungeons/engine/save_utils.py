#!/usr/bin/env python3
"""
Dungeon Master engine utilities.

The DM (AGENTS.md) invokes these functions to run any campaign:
  - dice rolls & combat helpers (deterministic, auditable)
  - create / load / save / autosave character sheets (game state)
  - validate a save against a campaign's stats schema (anti-cheat)
  - registry: list campaigns & saves, set/resume the current game
  - durable world/room state, death tracking, and "previously on" summaries

Everything is deterministic and auditable. The player NEVER calls these directly
and NEVER edits save files by hand -- the DM does, and only as a consequence of
in-fiction, schema-legal actions.

Design principle: stay GENERIC (works for any campaign/world type) but COMPLETE
enough to do its job. All game-specific meaning lives in the campaign schema and
world files, not in this engine.
"""
import argparse
import json
import os
import random
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths / config (overridable for testing)
# ---------------------------------------------------------------------------

ENGINE_DIR = Path(__file__).resolve().parent
DUNGEONS_DIR = ENGINE_DIR.parent            # .../dungeons  (distribution-owned engine dir)

# The engine now lives at <profile>/dungeons/, so the profile root is one level up.
PROFILE_ROOT = DUNGEONS_DIR.parent          # .../profiles/<profile>
_default_roots = [
    PROFILE_ROOT / "skills" / "campaigns",   # campaigns registered as skills
    DUNGEONS_DIR / "campaigns",              # optional content copies in workspace
]
_env_roots = os.environ.get("DUNGEON_CAMPAIGN_ROOTS")
CAMPAIGN_ROOTS = [Path(r) for r in _env_roots.split(os.pathsep)] if _env_roots else _default_roots

CURRENT_FILE = Path(os.environ.get(
    "DUNGEON_CURRENT_FILE", DUNGEONS_DIR / "saves" / ".current.json"))


def find_campaign_home(campaign_id, campaign_roots=None):
    """Locate a campaign's home dir from the registry roots, else default to first."""
    roots = campaign_roots if campaign_roots is not None else CAMPAIGN_ROOTS
    for root in roots:
        home = root / campaign_id
        if (home / "stats-schema.json").exists() or (home / "references" / "stats-schema.json").exists():
            return home
    return roots[0] / campaign_id


def campaign_schema_path(campaign_id, campaign_roots=None):
    home = find_campaign_home(campaign_id, campaign_roots)
    for candidate in (home / "stats-schema.json", home / "references" / "stats-schema.json"):
        if candidate.exists():
            return candidate
    return home / "references" / "stats-schema.json"


def save_dir_for(campaign, campaign_roots=None):
    """Saves live INSIDE the campaign folder so progress travels with the skill."""
    return find_campaign_home(campaign, campaign_roots) / "saves"


def save_path(campaign, slot, campaign_roots=None):
    return save_dir_for(campaign, campaign_roots) / f"{slot}.json"


# ---------------------------------------------------------------------------
# IO helpers (atomic writes for crash safety)
# ---------------------------------------------------------------------------

def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, obj):
    """Atomic write: write to a temp file, then rename over the target."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())
    shutil.move(str(tmp), str(path))


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Dice
# ---------------------------------------------------------------------------

DICE_RE = re.compile(r"^(\d*)d(\d+)([+-]\d+)?$", re.IGNORECASE)


def roll(spec):
    """Roll a dice spec like '2d6', '1d20+3', '3d6-1'. Returns (total, rolls)."""
    m = DICE_RE.match(spec.strip().replace(" ", ""))
    if not m:
        raise ValueError(f"Bad dice spec: {spec!r}")
    count = int(m.group(1) or "1")
    sides = int(m.group(2))
    mod = int(m.group(3) or 0)
    if count < 1 or sides < 1:
        raise ValueError(f"Bad dice spec: {spec!r}")
    rolls = [random.randint(1, sides) for _ in range(count)]
    return sum(rolls) + mod, rolls


def roll_d20():
    return random.randint(1, 20)


# ---------------------------------------------------------------------------
# Save creation / validation against a campaign schema
# ---------------------------------------------------------------------------

def new_save(schema, player_name):
    """Build a fresh character sheet from a campaign's stats schema."""
    stats = {}
    for stat in schema["stats"]:
        stats[stat["name"]] = stat.get("start", stat.get("min", 0))
    save = {
        "meta": {
            "campaign": schema["campaign"],
            "schema_version": schema.get("schema_version", 1),
            "player": player_name,
            "created": now_iso(),
            "updated": now_iso(),
            "turns": 0,
            "deaths": 0,
        },
        "stats": stats,
        "inventory": [],
        "abilities": [],
        "flags": {},
        "location": schema.get("start_location", "start"),
        "rooms": {},        # durable world state: room_id -> {explored, cleared, npcs{}}
        "log": [],
        "obituary": [],     # "previously on" summaries for resume
    }
    return save


def validate_save(save, schema):
    """Return a list of (problem, detail) tuples. Empty list == valid."""
    problems = []

    for stat in schema["stats"]:
        name = stat["name"]
        if name not in save.get("stats", {}):
            problems.append(("missing_stat", name))
            continue
        val = save["stats"][name]
        if not isinstance(val, (int, float)):
            problems.append(("non_numeric", f"{name}={val!r}"))
            continue
        if "min" in stat and val < stat["min"]:
            problems.append(("below_min", f"{name}={val} < {stat['min']}"))
        if "max" in stat and val > stat["max"]:
            problems.append(("above_max", f"{name}={val} > {stat['max']}"))
        if isinstance(val, float) and stat.get("type", "int") != "float":
            problems.append(("non_integer", name))

    known = {s["name"] for s in schema["stats"]}
    for name in save.get("stats", {}):
        if name not in known:
            problems.append(("unknown_stat", name))

    for deriv in schema.get("derived", []):
        expected = compute_derived(save, schema, deriv["expr"])
        got = save.get("stats", {}).get(deriv["target"])
        if got != expected:
            problems.append(("derived_mismatch", f"{deriv['target']}={got} expected {expected}"))

    allowed_items = set(schema.get("items", []))
    for item in save.get("inventory", []):
        if allowed_items and item not in allowed_items:
            problems.append(("unknown_item", item))
    allowed_ab = set(schema.get("abilities", []))
    for ab in save.get("abilities", []):
        if allowed_ab and ab not in allowed_ab:
            problems.append(("unknown_ability", ab))

    # Rooms must be a dict; if rooms referenced they live in schema rooms list.
    if not isinstance(save.get("rooms", {}), dict):
        problems.append(("rooms_not_dict", "rooms must be an object"))
    else:
        allowed_rooms = set(schema.get("rooms", []))
        for room in save.get("rooms", {}):
            if allowed_rooms and room not in allowed_rooms:
                problems.append(("unknown_room", room))

    return problems


def compute_derived(save, schema, expr):
    stats = save.get("stats", {})
    try:
        return int(eval(expr, {"__builtins__": {}}, stats))  # noqa: S307
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Registry / current-game pointer (session-to-session continuity)
# ---------------------------------------------------------------------------

def read_current():
    if CURRENT_FILE.exists():
        try:
            return load_json(CURRENT_FILE)
        except Exception:
            return None
    return None


def write_current(campaign, slot, summary=None):
    cur = read_current() or {}
    cur["campaign"] = campaign
    cur["slot"] = slot
    cur["updated"] = now_iso()
    if summary:
        cur["summary"] = summary
    # Always refresh the player from the authoritative save file.
    sp = save_path(campaign, slot)
    if sp.exists():
        try:
            cur["player"] = load_json(sp)["meta"]["player"]
        except Exception:
            pass
    elif "player" not in cur:
        cur["player"] = None
    write_json(CURRENT_FILE, cur)
    return cur


def list_campaigns(campaign_roots=None):
    """List campaign ids found in the registry roots (deduped, first-match order)."""
    roots = campaign_roots if campaign_roots is not None else CAMPAIGN_ROOTS
    seen = []
    for root in roots:
        cd = Path(root)
        if not cd.exists():
            continue
        for p in sorted(cd.iterdir()):
            if p.is_dir() and p.name not in seen and (
                (p / "stats-schema.json").exists() or (p / "references" / "stats-schema.json").exists()
            ):
                seen.append(p.name)
    return seen


def list_saves(campaign=None):
    """Discover saves by scanning each campaign's saves/ subdir (inside the skill)."""
    saves = {}
    for camp in list_campaigns():
        if campaign and camp != campaign:
            continue
        sdir = save_dir_for(camp)
        if not sdir.exists():
            continue
        slots = [p.stem for p in sorted(sdir.glob("*.json")) if not p.name.startswith(".")]
        if slots:
            saves[camp] = slots
    return saves


# ---------------------------------------------------------------------------
# Combat helpers (deterministic dice engine the DM narrates around)
# ---------------------------------------------------------------------------

def skill_check(stat_value, dc, bonus=0):
    """Roll 1d20 + stat + bonus vs a DC. Returns (success, natural, total)."""
    natural = roll_d20()
    total = natural + stat_value + bonus
    return natural >= 20 or total >= dc, natural, total


def initiative(entries):
    """Roll initiative for a list of ('name', bonus). Returns sorted (desc)."""
    results = []
    for name, bonus in entries:
        r = roll_d20()
        results.append((name, r + bonus, r))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


# ---------------------------------------------------------------------------
# World / room state helpers
# ---------------------------------------------------------------------------

def set_room(save, room_id, explored=None, cleared=None, npc_disp=None, npc=None):
    room = save.setdefault("rooms", {}).setdefault(room_id, {"explored": False, "cleared": False, "npcs": {}})
    if explored is not None:
        room["explored"] = bool(explored)
    if cleared is not None:
        room["cleared"] = bool(cleared)
    if npc_disp is not None and npc is not None:
        room.setdefault("npcs", {})[npc] = npc_disp
    return room


def touch_save(path, note=None, summary=None):
    save = load_json(path)
    save["meta"]["turns"] += 1
    save["meta"]["updated"] = now_iso()
    if note:
        save["log"].append({"turn": save["meta"]["turns"], "note": note})
    if summary:  # overwrite the "previously on" latest summary
        save["obituary"] = [summary] + [s for s in save.get("obituary", []) if s != summary]
    write_json(path, save)
    return save


def record_death(path, note=None):
    save = load_json(path)
    save["meta"]["deaths"] = save["meta"].get("deaths", 0) + 1
    save["meta"]["updated"] = now_iso()
    if note:
        save["log"].append({"turn": save["meta"].get("turns", 0), "death": note})
    write_json(path, save)
    return save


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_roll(args):
    for spec in args.specs:
        total, rolls = roll(spec)
        print(f"{spec} -> {rolls} = {total}")
    return 0


def cmd_check(args):
    success, natural, total = skill_check(args.stat, args.dc, args.bonus)
    verdict = "SUCCESS" if success else "FAIL"
    crit = " (natural 20!)" if natural == 20 else (" (natural 1!)" if natural == 1 else "")
    print(f"1d20={natural} + {args.stat} + {args.bonus} = {total} vs DC {args.dc} -> {verdict}{crit}")
    return 0 if success else 1


def cmd_initiative(args):
    entries = [(n, int(b)) for n, b in (e.split(":") for e in args.entries)]
    order = initiative(entries)
    for name, total, nat in order:
        print(f"{name}: {total} (roll {nat})")
    return 0


def cmd_new(args):
    schema = load_json(args.schema)
    save = new_save(schema, args.player)
    out = args.out or save_path(schema["campaign"], args.slot)
    write_json(out, save)
    write_current(schema["campaign"], args.slot)
    # Autosave = the new save IS written (atomic).
    print(f"Created {out}")
    return 0


def cmd_validate(args):
    schema = load_json(args.schema)
    save = load_json(args.save)
    problems = validate_save(save, schema)
    if not problems:
        print("VALID: save conforms to campaign schema.")
        return 0
    print(f"INVALID ({len(problems)} problem(s)):")
    for kind, detail in problems:
        print(f"  - {kind}: {detail}")
    return 1


def cmd_inspect(args):
    save = load_json(args.save)
    print(json.dumps(save, indent=2, ensure_ascii=False))
    return 0


def cmd_touch(args):
    save = touch_save(args.save, note=args.note, summary=args.summary)
    print(f"OK turn={save['meta']['turns']}")
    return 0


def cmd_autosave(args):
    src = args.save
    save = touch_save(src, note=None)
    write_json(src, save)
    write_current(save["meta"]["campaign"], Path(src).stem, summary=args.summary)
    print(f"AUTOSAVED turn={save['meta']['turns']}")
    return 0


def cmd_death(args):
    save = record_death(args.save, note=args.note)
    print(f"DEATH recorded: total={save['meta']['deaths']}")
    return 0


def cmd_list(args):
    cur = read_current()
    line = "Campaigns:"
    for c in list_campaigns():
        tag = c if cur and cur.get("campaign") == c else c
        line += f"  {tag}"
    print("Campaigns: " + (", ".join(list_campaigns()) or "(none on-disk)"))
    saves = list_saves(args.campaign)
    if not saves:
        print("Saves: (none)")
    else:
        for camp, slots in saves.items():
            cur_slot = cur.get("slot") if cur and cur.get("campaign") == camp else None
            marks = [f"{s}{'*' if s == cur_slot else ''}" for s in slots]
            print(f"Saves[{camp}]: {', '.join(marks)}")
    if cur:
        print(f"Current game: {cur.get('campaign')}/{cur.get('slot')} (player {cur.get('player')})")
        if cur.get("summary"):
            print(f"Previously on: {cur['summary']}")
    else:
        print("Current game: (none set)")
    return 0


def cmd_current(args):
    cur = read_current()
    if not cur:
        print("No current game set.")
        return 1
    print(f"campaign={cur.get('campaign')} slot={cur.get('slot')}")
    print(f"player={cur.get('player')} updated={cur.get('updated')}")
    if cur.get("summary"):
        print(f"summary={cur.get('summary')}")
    return 0


def cmd_resume(args):
    cur = read_current()
    if not cur:
        print("No current game set. Use 'new' or set one first.")
        return 1
    sp = save_path(cur["campaign"], cur["slot"])
    if not sp.exists():
        print(f"Save not found: {sp}")
        return 1
    save = load_json(sp)
    print(f"Resuming {cur['campaign']}/{cur['slot']} as {save['meta']['player']}")
    print(f"Location: {save['location']}  HP: {save['stats'].get('hp')}  Turns: {save['meta']['turns']}")
    if cur.get("summary"):
        print(f"Previously on: {cur['summary']}")
    elif save.get("obituary"):
        print(f"Previously on: {save['obituary'][0]}")
    return 0


def cmd_use(args):
    if args.campaign and args.slot:
        write_current(args.campaign, args.slot, summary=args.summary)
        print(f"Current game set: {args.campaign}/{args.slot}")
        return 0
    # interactive selection
    campaigns = list_campaigns()
    print("Campaigns:", ", ".join(campaigns) or "(none)")
    return 0


def cmd_room(args):
    save = load_json(args.save)
    set_room(save, args.room, explored=args.explored, cleared=args.cleared,
             npc_disp=args.npc, npc=args.npc_name)
    write_json(args.save, save)
    print(f"Room state updated: {args.room}")
    print(json.dumps(save["rooms"].get(args.room), indent=2))
    return 0


def build_parser():
    p = argparse.ArgumentParser(description="Dungeon Master engine utils")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("roll", help="roll dice, e.g. roll 2d6+1")
    r.add_argument("specs", nargs="+")
    r.set_defaults(func=cmd_roll)

    c = sub.add_parser("check", help="skill check: 1d20 + stat + bonus vs DC")
    c.add_argument("--stat", type=int, required=True)
    c.add_argument("--dc", type=int, required=True)
    c.add_argument("--bonus", type=int, default=0)
    c.set_defaults(func=cmd_check)

    ini = sub.add_parser("initiative", help="roll initiative, entries as name:bonus")
    ini.add_argument("entries", nargs="+", help="e.g. 'Thorn:2' 'goblin:0'")
    ini.set_defaults(func=cmd_initiative)

    n = sub.add_parser("new", help="create a fresh save from a campaign schema")
    n.add_argument("--schema", required=True)
    n.add_argument("--player", required=True)
    n.add_argument("--slot", required=True)
    n.add_argument("--saves-dir")
    n.add_argument("--out")
    n.set_defaults(func=cmd_new)

    v = sub.add_parser("validate", help="validate a save against a schema")
    v.add_argument("--schema", required=True)
    v.add_argument("--save", required=True)
    v.set_defaults(func=cmd_validate)

    i = sub.add_parser("inspect", help="pretty-print a save")
    i.add_argument("--save", required=True)
    i.set_defaults(func=cmd_inspect)

    t = sub.add_parser("touch", help="advance turn + append log note/summary")
    t.add_argument("--save", required=True)
    t.add_argument("--note")
    t.add_argument("--summary")
    t.set_defaults(func=cmd_touch)

    a = sub.add_parser("autosave", help="save + update current-game pointer")
    a.add_argument("--save", required=True)
    a.add_argument("--summary")
    a.set_defaults(func=cmd_autosave)

    d = sub.add_parser("death", help="record a death (increment counter)")
    d.add_argument("--save", required=True)
    d.add_argument("--note")
    d.set_defaults(func=cmd_death)

    l = sub.add_parser("list", help="list campaigns, saves, current game")
    l.add_argument("--campaign")
    l.set_defaults(func=cmd_list)

    cu = sub.add_parser("current", help="show current game pointer")
    cu.set_defaults(func=cmd_current)

    rs = sub.add_parser("resume", help="print resume info for the current game")
    rs.set_defaults(func=cmd_resume)

    u = sub.add_parser("use", help="set the current game (campaign slot)")
    u.add_argument("--campaign")
    u.add_argument("--slot")
    u.add_argument("--summary")
    u.set_defaults(func=cmd_use)

    rm = sub.add_parser("room", help="update durable room/world state")
    rm.add_argument("--save", required=True)
    rm.add_argument("--room", required=True)
    rm.add_argument("--explored", action="store_true")
    rm.add_argument("--cleared", action="store_true")
    rm.add_argument("--npc-name")
    rm.add_argument("--npc", help="disposition e.g. hostile/friendly/unknown")
    rm.set_defaults(func=cmd_room)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
