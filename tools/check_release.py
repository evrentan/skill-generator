#!/usr/bin/env python3
"""Check that the plugin manifests and the skill copy of LICENSE are in sync.

Usage: python tools/check_release.py   (from the repository root)
"""

import filecmp
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "skill-generator"
VERSIONED = ["plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json", ".cursor-plugin/plugin.json"]
UNVERSIONED = [".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"]


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def main():
    match = re.search(r'^\s+version:\s*"([^"]+)"', (SKILL / "SKILL.md").read_text(encoding="utf-8"), re.M)
    if not match:
        sys.exit("SKILL.md: metadata.version not found")
    version = match.group(1)
    found = {rel: load(rel).get("version") for rel in VERSIONED}
    cursor = load(".cursor-plugin/marketplace.json")
    found[".cursor-plugin/marketplace.json metadata"] = cursor.get("metadata", {}).get("version")
    found[".cursor-plugin/marketplace.json plugins[0]"] = cursor.get("plugins", [{}])[0].get("version")
    for rel in UNVERSIONED:
        load(rel)
    errors = [f"{name}: version {got!r}, SKILL.md has {version!r}" for name, got in found.items() if got != version]
    if not filecmp.cmp(ROOT / "LICENSE", SKILL / "LICENSE", shallow=False):
        errors.append("skills/skill-generator/LICENSE differs from LICENSE")
    if errors:
        sys.exit("\n".join(errors))
    print(f"OK: version {version}, LICENSE in sync")


if __name__ == "__main__":
    main()
