#!/usr/bin/env python3
"""Validate the structure of an agent skill folder.

Usage: python3 quick_validate.py <skill_directory>

Errors (exit 1): problems that break loading or triggering.
Warnings (exit 0): best-practice issues worth a look.
Uses PyYAML when installed, otherwise a small built-in frontmatter parser.
"""

import re
import sys
from pathlib import Path

PORTABLE_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
KNOWN_EXTENSION_KEYS = {
    "argument-hint", "model", "triggers", "permissions", "subagent", "agent",
    "disable-model-invocation", "user-invocable", "context", "hooks",
}
MAX_BODY_LINES = 500
RESOURCE_DIRS = ("scripts", "references", "assets", "agents")


def _unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def _parse_frontmatter_fallback(text):
    data, lines, i = {}, text.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            if line.strip() and not line.lstrip().startswith("#"):
                raise ValueError(f"cannot parse line {i + 1}: {line!r}")
            i += 1
            continue
        key, raw = match.group(1), match.group(2).strip()
        i += 1
        block = []
        while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
            block.append(lines[i])
            i += 1
        while block and not block[-1].strip():
            block.pop()
        if raw[:1] in (">", "|"):
            parts = [b.strip() for b in block]
            data[key] = (" " if raw[0] == ">" else "\n").join(parts).strip()
        elif raw.startswith("[") and raw.endswith("]"):
            data[key] = [_unquote(v) for v in raw[1:-1].split(",") if v.strip()]
        elif raw:
            data[key] = _unquote(raw)
        elif block and block[0].strip().startswith("- "):
            data[key] = [_unquote(b.strip()[2:]) for b in block if b.strip().startswith("- ")]
        elif block:
            data[key] = {"_raw": "\n".join(block)}
        else:
            data[key] = ""
    return data


def parse_frontmatter(text):
    try:
        import yaml  # type: ignore
    except ImportError:
        return _parse_frontmatter_fallback(text)
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    return data


def validate(skill_dir):
    errors, warnings = [], []
    skill_dir = Path(skill_dir).expanduser().resolve()
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"SKILL.md not found in {skill_dir}"], warnings

    content = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", content, re.DOTALL)
    if not match:
        return ["SKILL.md must start with YAML frontmatter delimited by '---' lines"], warnings
    fm_text, body = match.groups()

    try:
        fm = parse_frontmatter(fm_text)
    except Exception as exc:
        return [f"invalid frontmatter: {exc}"], warnings

    name = fm.get("name")
    if not name:
        errors.append("missing 'name'")
    elif not isinstance(name, str):
        errors.append(f"'name' must be a string, got {type(name).__name__}")
    else:
        name = name.strip()
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
            errors.append(f"name '{name}' must be kebab-case: lowercase letters/digits, single hyphens, no leading/trailing hyphen")
        if len(name) > 64:
            errors.append(f"name is {len(name)} chars; max 64")
        if name != skill_dir.name:
            warnings.append(f"name '{name}' differs from folder name '{skill_dir.name}'")

    desc = fm.get("description")
    if not desc:
        errors.append("missing 'description'")
    elif not isinstance(desc, str):
        errors.append(f"'description' must be a string, got {type(desc).__name__}")
    else:
        desc = desc.strip()
        if "<" in desc or ">" in desc:
            errors.append("description must not contain angle brackets (< or >)")
        if len(desc) > 1024:
            errors.append(f"description is {len(desc)} chars; max 1024")
        if len(desc) < 80:
            warnings.append("description is very short; include both what the skill does and when to use it")
        if not re.search(r"\b(use|used|when|whenever|if the user|load|invoke|trigger)\b", desc, re.IGNORECASE):
            warnings.append("description doesn't seem to say WHEN to use the skill")

    compat = fm.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str):
            errors.append("'compatibility' must be a string")
        elif len(compat) > 500:
            errors.append(f"compatibility is {len(compat)} chars; max 500")

    for key in sorted(set(fm) - PORTABLE_KEYS):
        if key in KNOWN_EXTENSION_KEYS:
            warnings.append(f"'{key}' is a harness-specific extension; other harnesses may ignore it")
        else:
            warnings.append(f"unknown frontmatter key '{key}'")

    body_lines = body.count("\n") + 1
    if not body.strip():
        errors.append("SKILL.md body is empty")
    elif body_lines > MAX_BODY_LINES:
        warnings.append(f"body is {body_lines} lines; consider moving detail into references/ (target < {MAX_BODY_LINES})")

    all_text = content + "".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for d in RESOURCE_DIRS for p in (skill_dir / d).rglob("*.md") if p.is_file()
    )
    pattern = r"(?<![\w./-])((?:%s)/[\w./-]+\.\w+)" % "|".join(RESOURCE_DIRS)
    for ref in sorted(set(re.findall(pattern, content))):
        if not (skill_dir / ref).exists():
            warnings.append(f"referenced file not found: {ref}")

    for d in RESOURCE_DIRS:
        for path in (skill_dir / d).rglob("*") if (skill_dir / d).is_dir() else []:
            if path.is_file() and "__pycache__" not in path.parts:
                rel = path.relative_to(skill_dir).as_posix()
                if rel not in all_text and path.name not in all_text:
                    warnings.append(f"bundled file never referenced: {rel}")

    secret_pattern = r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"
    if re.search(secret_pattern, content):
        warnings.append("SKILL.md may contain a hard-coded secret")

    cred_name = re.compile(r"(?i)^(secrets?|\.env.*|.*\.(key|pem|p12|pfx)|.*(token|webhook|credential|password).*)$")
    cred_paths = sorted(
        p.relative_to(skill_dir).as_posix() for p in skill_dir.rglob("*")
        if cred_name.match(p.name) and "-workspace" not in p.as_posix()
    )
    if cred_paths:
        warnings.append(
            "credential-like files inside the skill folder (names only, not read): "
            + ", ".join(cred_paths[:5]) + (" ..." if len(cred_paths) > 5 else "")
            + ". Exclude them from copies/packages, and make sure SKILL.md says so"
        )

    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 quick_validate.py <skill_directory>")
        sys.exit(2)
    errors, warnings = validate(sys.argv[1])
    for e in errors:
        print(f"ERROR:   {e}")
    for w in warnings:
        print(f"WARNING: {w}")
    if errors:
        print(f"\nInvalid: {len(errors)} error(s), {len(warnings)} warning(s)")
        sys.exit(1)
    print(f"Valid{f' with {len(warnings)} warning(s)' if warnings else ''}.")


if __name__ == "__main__":
    main()
