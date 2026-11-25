#!/usr/bin/env python3
"""Check classes.json, stage prepared bodies for publishing, and pin their hashes.

  python3 tools/models.py check [--weapons DIR] [--files]   validate the manifest; --files also hashes assets/models/
  python3 tools/models.py stage DIR [DIR...]                copy each class's prepared kit GLB (and .webp.glb) into
                                                            assets/models/ under the manifest's file names
  python3 tools/models.py pin                               write bytes and sha256 of the staged files into classes.json

stage looks in every DIR (recursively) for `<body_id>.glb`, then `<prep name>_kit.glb`, where the prep name is the
prep config's base name (swat.json -> swat_kit.glb), the names gs-player-char's tools/avatar_prep/kit_rig.py writes.
Loadout ids are checked against fc-weapons' IDS when a checkout is beside this one (or at --weapons); CI has none
and skips that part, saying so.
"""
import hashlib
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(HERE, "classes.json")
MODELS = os.path.join(HERE, "assets", "models")
CLASS_KEYS = {"id", "display_name", "team", "side", "description", "body_id", "credits", "model", "lods", "skeleton",
              "arms", "stats", "loadout"}
MODEL_KEYS = {"file", "bytes", "sha256", "web_file", "web_bytes", "web_sha256"}
STAT_KEYS = {"health", "speed", "sprint_speed_scale", "jump_scale"}


def load():
    with open(MANIFEST) as f:
        return json.load(f)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def weapon_ids(where):
    pack = os.path.join(where, "addons", "fc_weapons", "aw_weapon_pack.gd")
    if not os.path.isfile(pack):
        return None
    src = open(pack).read()
    m = re.search(r"const IDS: Array\[StringName\] = \[(.*?)\]", src, re.S)
    return set(re.findall(r'&"([a-z0-9_]+)"', m.group(1))) if m else None


def check(args):
    errors = []
    data = load()
    weapons_dir = os.path.join(HERE, "..", "fc-weapons")
    if "--weapons" in args:
        weapons_dir = args[args.index("--weapons") + 1]
    ids = weapon_ids(weapons_dir)
    if data.get("schema") != 1:
        errors.append("schema must be 1")
    seen, teams = set(), set()
    for c in data.get("classes", []):
        cid = c.get("id", "?")
        missing = CLASS_KEYS - set(c)
        if missing:
            errors.append("%s: missing %s" % (cid, ", ".join(sorted(missing))))
            continue
        if cid in seen:
            errors.append("%s: duplicate id" % cid)
        seen.add(cid)
        if c["team"] in teams:
            errors.append("%s: team %s already has a class" % (cid, c["team"]))
        teams.add(c["team"])
        if MODEL_KEYS - set(c["model"]):
            errors.append("%s: model needs %s" % (cid, ", ".join(sorted(MODEL_KEYS - set(c["model"])))))
        if c["model"].get("file") != c["body_id"] + ".glb":
            errors.append("%s: model.file must be <body_id>.glb (FC registers bodies by file name)" % cid)
        if [l.get("name") for l in c["lods"]] != ["LOD%d" % i for i in range(len(c["lods"]))]:
            errors.append("%s: lods must be LOD0..LODn in order" % cid)
        if STAT_KEYS - set(c["stats"]):
            errors.append("%s: stats need %s" % (cid, ", ".join(sorted(STAT_KEYS - set(c["stats"])))))
        refs = [w for group in c["loadout"].values() for w in group]
        if ids is not None:
            for w in refs:
                if w not in ids:
                    errors.append("%s: loadout id %r is not an fc-weapons id" % (cid, w))
        for key in ("sha256", "web_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", str(c["model"].get(key, ""))):
                errors.append("%s: model.%s is not pinned (tools/models.py pin)" % (cid, key))
        if "--files" in args:
            for f, b, s in (("file", "bytes", "sha256"), ("web_file", "web_bytes", "web_sha256")):
                p = os.path.join(MODELS, c["model"][f])
                if not os.path.isfile(p):
                    errors.append("%s: %s not fetched (./fetch-content.sh)" % (cid, c["model"][f]))
                elif os.path.getsize(p) != c["model"][b] or sha256(p) != c["model"][s]:
                    errors.append("%s: %s does not match the manifest" % (cid, c["model"][f]))
    for e in errors:
        print("classes.json: " + e, file=sys.stderr)
    note = "" if ids is not None else " (fc-weapons not beside: loadout ids not checked)"
    print("classes.json: %d classes, %d errors%s" % (len(seen), len(errors), note))
    return 1 if errors else 0


def stage(dirs):
    if not dirs:
        print("usage: tools/models.py stage DIR [DIR...]", file=sys.stderr)
        return 2
    os.makedirs(MODELS, exist_ok=True)
    found = {}
    for d in dirs:
        for root, _, files in os.walk(d):
            for f in files:
                found.setdefault(f, os.path.join(root, f))
    bad = 0
    for c in load()["classes"]:
        prep = os.path.splitext(os.path.basename(c["skeleton"]["prep_config"]))[0]
        for want, names in ((c["model"]["file"], [c["body_id"] + ".glb", prep + "_kit.glb"]),
                            (c["model"]["web_file"], [c["body_id"] + ".webp.glb", prep + "_kit.webp.glb"])):
            src = next((found[n] for n in names if n in found), None)
            if not src:
                print("stage: %s: none of %s in %s" % (c["id"], ", ".join(names), " ".join(dirs)), file=sys.stderr)
                bad = 1
                continue
            shutil.copyfile(src, os.path.join(MODELS, want))
            print("stage: %s <- %s" % (want, src))
    return bad


def pin(_args):
    data = load()
    for c in data["classes"]:
        for f, b, s in (("file", "bytes", "sha256"), ("web_file", "web_bytes", "web_sha256")):
            p = os.path.join(MODELS, c["model"][f])
            if not os.path.isfile(p):
                print("pin: %s missing; run stage first" % p, file=sys.stderr)
                return 1
            c["model"][b] = os.path.getsize(p)
            c["model"][s] = sha256(p)
    with open(MANIFEST, "w") as f:
        json.dump(data, f, indent=4)
        f.write("\n")
    print("pin: wrote %d classes" % len(data["classes"]))
    return 0


if __name__ == "__main__":
    verb, rest = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("check", [])
    fn = {"check": check, "stage": stage, "pin": pin}.get(verb)
    if not fn:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(fn(rest))
