#!/usr/bin/env python3
"""
Shape versioning manifest (decision 004).

Content-hashes every block .ttl + routes.json. `update` appends a new version
entry (with per-file hash diff vs the previous version) when anything changed;
`verify` checks the working files against the latest recorded version. Audit
runs stamp the manifest version + combined hash they executed under.

USAGE:
  python3 shape_manifest.py update
  python3 shape_manifest.py verify
"""
import glob
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "shapes_manifest.json")


def file_hashes():
    files = sorted(glob.glob(os.path.join(HERE, "blocks", "*.ttl")))
    files.append(os.path.join(HERE, "routes.json"))
    hashes = {}
    for path in files:
        with open(path, "rb") as f:
            hashes[os.path.relpath(path, HERE)] = hashlib.sha256(f.read()).hexdigest()
    return hashes


def combined_hash(hashes):
    payload = json.dumps(hashes, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def load_manifest():
    if os.path.exists(MANIFEST):
        with open(MANIFEST) as f:
            return json.load(f)
    return {"versions": []}


def timestamp():
    # deterministic-environment-friendly: file mtime of newest shape file
    files = sorted(glob.glob(os.path.join(HERE, "blocks", "*.ttl")))
    newest = max(os.path.getmtime(p) for p in files)
    return subprocess.run(
        ["date", "-r", str(int(newest)), "+%Y-%m-%dT%H:%M:%S"],
        capture_output=True, text=True).stdout.strip()


def update():
    manifest = load_manifest()
    hashes = file_hashes()
    combo = combined_hash(hashes)
    if manifest["versions"] and manifest["versions"][-1]["combined_sha256"] == combo:
        print("No change: still version %d (%s)"
              % (manifest["versions"][-1]["version"], combo[:12]))
        return
    prev = manifest["versions"][-1]["files"] if manifest["versions"] else {}
    changed = sorted(f for f in hashes if hashes[f] != prev.get(f))
    removed = sorted(f for f in prev if f not in hashes)
    entry = {"version": len(manifest["versions"]) + 1,
             "timestamp": timestamp(),
             "combined_sha256": combo,
             "files": hashes,
             "changed_files": changed, "removed_files": removed}
    manifest["versions"].append(entry)
    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
    print("Recorded shapes version %d (%s); changed: %s"
          % (entry["version"], combo[:12], ", ".join(changed) or "-"))


def current_version():
    """Return (version_number, combined_hash) of latest manifest entry, verifying it."""
    manifest = load_manifest()
    if not manifest["versions"]:
        raise SystemExit("No shapes_manifest.json version recorded — run: shape_manifest.py update")
    latest = manifest["versions"][-1]
    if combined_hash(file_hashes()) != latest["combined_sha256"]:
        raise SystemExit(
            "Shapes on disk do NOT match manifest version %d — an SME edited shapes "
            "without recording a version. Run: shape_manifest.py update" % latest["version"])
    return latest["version"], latest["combined_sha256"]


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verify"
    if cmd == "update":
        update()
    else:
        v, h = current_version()
        print("Shapes verified: version %d (%s)" % (v, h[:12]))
