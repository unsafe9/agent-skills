#!/usr/bin/env python3
"""Validate an Alfred workflow folder (or a bare info.plist).

Checks plist syntax, required keys, object/connection/uidata consistency, canvas
overlaps, and the known silent-failure mistakes of hand-built workflows.

Usage: validate.py <workflow-dir | info.plist> [--json]
Exit code: 0 = no errors (warnings allowed), 1 = errors found.
"""
import json
import os
import plistlib
import re
import subprocess
import sys

UUID_RE = re.compile(r"^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$")
VERIFIED_SCRIPT_TYPES = {0: "/bin/bash", 2: "/usr/bin/ruby", 7: "osascript JXA",
                         8: "external script", 11: "/bin/zsh"}
SCRIPT_OBJECT_TYPES = {"alfred.workflow.input.scriptfilter", "alfred.workflow.action.script"}
# Approximate Alfred 5 canvas footprints (px), anchored at uidata xpos/ypos and
# extending right/down. Overlap = a true AABB intersection of these boxes, so the
# recommended grid (x+200 / y+150, layout.md) clears every pair while bunched or
# tucked-in nodes intersect and get flagged. Sizes calibrated to a 5.7.3 canvas:
# a tile is the icon + title (taller than the old 90×60 guess), a `note` adds a row,
# automation/hexagon objects render ~3x taller, and a Conditional grows per output.
STD_W, STD_H = 150, 110
NOTE_H = 35
LARGE_W, LARGE_H = 180, 190
JUNCTION_W, JUNCTION_H = 70, 60
COND_BASE_H, COND_ROW_H = 90, 50
LARGE_TILE_TYPES = {
    "alfred.workflow.automation.task",
    "alfred.workflow.automation.runshortcut",
    "alfred.workflow.action.systemcommand",
    "alfred.workflow.action.itunescommand",
}


def footprint(obj, entry):
    """(width, height) the object occupies on the canvas, given its uidata entry."""
    t = obj.get("type", "")
    name = t.split(".")[-1]
    if t in LARGE_TILE_TYPES:
        w, h = LARGE_W, LARGE_H
    elif name == "junction":
        w, h = JUNCTION_W, JUNCTION_H
    elif name == "conditional":
        n = len(obj.get("config", {}).get("conditions", []) or [])
        w, h = STD_W, max(STD_H, COND_BASE_H + COND_ROW_H * (n + 1))  # outputs + else
    else:
        w, h = STD_W, STD_H
    if isinstance(entry, dict) and entry.get("note"):
        h += NOTE_H
    return w, h

errors, warnings, infos = [], [], []
err, warn, info = errors.append, warnings.append, infos.append


def label(obj):
    return f"{obj.get('type', '?').split('.')[-1]}[{obj.get('uid', '?')[:8]}]"


def check_objects(d, wf_dir):
    by_uid = {}
    cond_outputs = {}  # object uid -> set of condition uids
    for i, obj in enumerate(d.get("objects", [])):
        for k in ("type", "uid", "version"):
            if k not in obj:
                err(f"objects[{i}] missing key '{k}'")
        uid = obj.get("uid", "")
        if uid in by_uid:
            err(f"duplicate object uid {uid}")
        by_uid[uid] = obj
        if not UUID_RE.match(uid):
            warn(f"{label(obj)}: uid is not an UPPERCASE UUID ('{uid}')")
        otype = obj.get("type", "")
        cfg = obj.get("config")
        if cfg is None and otype != "alfred.workflow.utility.junction":
            warn(f"{label(obj)}: has no config dict (only junction omits config)")

        if otype in SCRIPT_OBJECT_TYPES and cfg is not None:
            stype = cfg.get("type")
            if stype not in VERIFIED_SCRIPT_TYPES:
                warn(f"{label(obj)}: script type {stype!r} is not a verified interpreter "
                     f"(verified: {VERIFIED_SCRIPT_TYPES}); copy from a real workflow or use a shell shim")
            if cfg.get("scriptargtype") == 0:
                warn(f"{label(obj)}: scriptargtype=0 ({{query}} substitution) — prefer 1 (argv), no escaping issues")
            script, scriptfile = cfg.get("script", ""), cfg.get("scriptfile", "")
            if not script and not scriptfile:
                err(f"{label(obj)}: both script and scriptfile are empty")
            if script and scriptfile:
                warn(f"{label(obj)}: both script and scriptfile set — empty the unused one")
            if scriptfile and stype != 8:
                err(f"{label(obj)}: scriptfile is set but type={stype} — external script files run "
                    f"only with type=8; any other type runs the inline script instead (silently "
                    f"empty results when inline is empty)")
            if stype == 8 and not scriptfile:
                err(f"{label(obj)}: type=8 (External Script) but scriptfile is empty")
            if "script" not in cfg or "scriptfile" not in cfg:
                warn(f"{label(obj)}: keep both 'script' and 'scriptfile' keys present (unused one empty)")
            if scriptfile and wf_dir:
                p = os.path.join(wf_dir, scriptfile)
                if not os.path.exists(p):
                    err(f"{label(obj)}: scriptfile '{scriptfile}' not found in workflow folder")
                elif not os.access(p, os.X_OK):
                    err(f"{label(obj)}: scriptfile '{scriptfile}' is not executable (chmod +x)")

        if otype == "alfred.workflow.input.listfilter" and cfg is not None:
            try:
                json.loads(cfg.get("items", ""))
            except (TypeError, ValueError):
                err(f"{label(obj)}: listfilter 'items' must be a JSON string (array of objects)")

        if otype == "alfred.workflow.automation.task" and cfg is not None:
            taskuid = cfg.get("taskuid", "")
            if not taskuid:
                err(f"{label(obj)}: automation task missing taskuid")
            else:
                cat = os.path.expanduser("~/Library/Application Support/Alfred/Automation/Tasks")
                if os.path.isdir(cat) and not os.path.isfile(os.path.join(cat, taskuid, "alfredtask.json")):
                    warn(f"{label(obj)}: taskuid '{taskuid}' not found in the local Automation Tasks "
                         f"catalog — it would silently no-op on this machine")

        if otype == "alfred.workflow.utility.conditional" and cfg is not None:
            uids = {c.get("uid") for c in cfg.get("conditions", []) if isinstance(c, dict)}
            if not uids:
                err(f"{label(obj)}: conditional has no conditions")
            cond_outputs[uid] = uids
    return by_uid, cond_outputs


def check_connections(d, by_uid, cond_outputs):
    incoming, outgoing = set(), {}
    for src, conns in d.get("connections", {}).items():
        if src not in by_uid:
            err(f"connections: source uid {src} is not an object")
            continue
        outgoing[src] = []
        for c in conns:
            dest = c.get("destinationuid")
            if not dest:
                err(f"connections[{src[:8]}]: edge missing destinationuid")
                continue
            if dest not in by_uid:
                err(f"connections[{src[:8]}]: destination {dest} is not an object")
                continue
            incoming.add(dest)
            outgoing[src].append(dest)
            if "vetoclose" in c:
                err(f"connections[{src[:8]}→{dest[:8]}]: key must be spelled 'vitoclose' (Alfred's own typo), not 'vetoclose'")
            for k in ("modifiers", "modifiersubtext", "vitoclose"):
                if k not in c:
                    warn(f"connections[{src[:8]}→{dest[:8]}]: missing '{k}'")
            sou = c.get("sourceoutputuid")
            if sou is not None:
                valid = cond_outputs.get(src, set())
                if sou not in valid:
                    err(f"connections[{src[:8]}→{dest[:8]}]: sourceoutputuid {sou[:8]}… does not match any "
                        f"condition uid of the source conditional")
    return incoming, outgoing


def check_graph(by_uid, incoming, outgoing):
    entries = {u for u, o in by_uid.items()
               if o.get("type", "").startswith(("alfred.workflow.trigger.", "alfred.workflow.input."))}
    if not entries:
        err("workflow has no trigger or input object — nothing can start it")
    seen, stack = set(), list(entries)
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        stack.extend(outgoing.get(u, []))
    for u, o in by_uid.items():
        if u not in seen:
            warn(f"{label(o)}: unreachable from any trigger/input")
        cat = o.get("type", "").split(".")[2] if o.get("type", "").count(".") >= 2 else ""
        if cat in ("utility", "automation") and not outgoing.get(u):
            warn(f"{label(o)}: {cat} node has no outgoing connection (dead end)")


def check_uidata(d, by_uid, outgoing):
    ui = d.get("uidata", {})
    pos = {}
    for u, o in by_uid.items():
        entry = ui.get(u)
        if not isinstance(entry, dict) or "xpos" not in entry or "ypos" not in entry:
            err(f"{label(o)}: missing uidata entry with xpos/ypos (lands at 0,0 on the canvas)")
            continue
        pos[u] = (float(entry["xpos"]), float(entry["ypos"]))
    for u in ui:
        if u not in by_uid:
            warn(f"uidata entry {u[:8]}… has no matching object")
    box = {u: footprint(by_uid[u], ui.get(u)) for u in pos}
    uids = list(pos)
    for i, a in enumerate(uids):
        ax, ay = pos[a]; aw, ah = box[a]
        for b in uids[i + 1:]:
            bx, by = pos[b]; bw, bh = box[b]
            if ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah:
                ox = min(ax + aw, bx + bw) - max(ax, bx)
                oy = min(ay + ah, by + bh) - max(ay, by)
                warn(f"canvas overlap: {label(by_uid[a])} and {label(by_uid[b])} "
                     f"intersect by {ox:.0f}×{oy:.0f}px — space them on the grid (layout.md)")
    for src, dests in outgoing.items():
        for dest in dests:
            if src in pos and dest in pos and pos[dest][0] <= pos[src][0]:
                warn(f"backwards edge on canvas: {label(by_uid[src])} → {label(by_uid[dest])} "
                     f"does not flow left→right")


def check_userconfig(d):
    for i, item in enumerate(d.get("userconfigurationconfig", [])):
        for k in ("type", "variable", "label", "config"):
            if k not in item:
                err(f"userconfigurationconfig[{i}] missing '{k}'")
        cfg = item.get("config", {})
        if item.get("type") == "popupbutton":
            values = [p[1] for p in cfg.get("pairs", []) if isinstance(p, list) and len(p) == 2]
            if cfg.get("default") not in values:
                err(f"userconfigurationconfig[{i}] ({item.get('variable')}): popupbutton default "
                    f"{cfg.get('default')!r} not among pair values {values}")
        if item.get("type") == "checkbox" and "text" not in cfg:
            warn(f"userconfigurationconfig[{i}] ({item.get('variable')}): checkbox uses config key 'text' for its label")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if not args:
        print(__doc__)
        return 2
    path = args[0]
    if os.path.isdir(path):
        wf_dir, plist_path = path, os.path.join(path, "info.plist")
    else:
        wf_dir, plist_path = os.path.dirname(os.path.abspath(path)), path
    if not os.path.exists(plist_path):
        print(f"ERROR: {plist_path} not found")
        return 1

    lint = subprocess.run(["plutil", "-lint", plist_path], capture_output=True, text=True)
    if lint.returncode != 0:
        err(f"plutil -lint: {(lint.stdout + lint.stderr).strip()}")

    d = None
    try:
        with open(plist_path, "rb") as f:
            d = plistlib.load(f)
    except Exception as e:
        err(f"plist parse failed: {e}")

    if d is not None:
        for k in ("bundleid", "name", "objects", "connections", "uidata"):
            if k not in d:
                err(f"missing top-level key: {k}")
        if d.get("bundleid") and "." not in d["bundleid"]:
            warn("bundleid should be reverse-DNS (com.you.workflowname)")
        if "userconfigurationconfig" not in d:
            warn("add 'userconfigurationconfig' (empty array is fine) — Alfred 5 workflows carry it")
        if "objects" in d:
            by_uid, cond_outputs = check_objects(d, wf_dir if os.path.isdir(path) else None)
            incoming, outgoing = check_connections(d, by_uid, cond_outputs)
            check_graph(by_uid, incoming, outgoing)
            check_uidata(d, by_uid, outgoing)
        check_userconfig(d)
        if os.path.isdir(path) and not os.path.exists(os.path.join(wf_dir, "icon.png")):
            warn("no icon.png — workflow shows a generic gear everywhere; see packaging.md § Icon")

    if as_json:
        print(json.dumps({"errors": errors, "warnings": warnings, "infos": infos}, indent=2))
    else:
        for tag, items in (("ERROR", errors), ("WARN", warnings), ("INFO", infos)):
            for m in items:
                print(f"{tag}: {m}")
        print(f"\n{'FAIL' if errors else 'PASS'}: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
