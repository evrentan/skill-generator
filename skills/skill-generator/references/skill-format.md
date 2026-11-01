# Skill Format Reference

Read this when writing a new skill or auditing an existing one.

## Contents

1. Folder structure
2. Frontmatter — portable fields
3. Frontmatter — harness-specific extensions
4. Where skills live
5. Writing the description
6. Writing the body
7. Bundled resources
8. Audit checklist
9. Minimal templates

---

## 1. Folder structure

```
<skill-name>/
├── SKILL.md            required: YAML frontmatter + Markdown body
├── scripts/            optional: executable helpers (python, bash, node)
├── references/         optional: docs read on demand
├── assets/             optional: templates, images, fonts used in outputs
└── evals/              optional: evals.json, trigger_evals.json, files/
```

- The folder name is the skill's identifier and should equal `name` in the frontmatter.
- `SKILL.md` must start with `---` on line 1.
- Reference bundled files with paths relative to the skill folder (`scripts/fill_form.py`), and tell the agent *when* to read or run each one.

## 2. Frontmatter — portable fields

These follow the open Agent Skills format and are understood broadly.

| Field | Required | Rules |
|---|---|---|
| `name` | yes | kebab-case `[a-z0-9-]`, no leading/trailing/double hyphens, ≤ 64 chars, equals folder name |
| `description` | yes | ≤ 1024 chars, no `<` or `>`, says what it does AND when to use it |
| `license` | no | license name or pointer to a bundled license file |
| `compatibility` | no | ≤ 500 chars; environment requirements (e.g. "needs python3 and network access") |
| `metadata` | no | free-form map: `version`, `author`, `tags`, ... |
| `allowed-tools` | no | tools the skill expects/pre-approves; semantics vary by harness (pre-approval in some, nothing in others) |

Use a quoted string or a folded scalar (`description: >-`) for long descriptions so colons and special characters don't break YAML.

## 3. Frontmatter — harness-specific extensions

Only add these if the user targets that harness. Other harnesses generally ignore unknown keys, but keep them minimal so the skill stays portable. When updating a skill, **preserve** extension keys you find — they were put there on purpose. Always check the harness's current docs; these change.

Examples seen in the wild:

- **Claude Code**: `allowed-tools`, `argument-hint`, `model`, `disable-model-invocation`, `user-invocable`
- **Devin CLI**: `argument-hint`, `model`, `triggers` (`user`, `model`), `permissions` (`allow`/`deny`/`ask`), `subagent`, `agent`
- **Windsurf/Cascade**: reads the same `SKILL.md` format from its skills folders

Common intent → typical mechanism:

- "Only run when I type /skill-name" → disable model invocation (`triggers: [user]`, `disable-model-invocation: true`, ...)
- "Don't prompt me for read/grep" → `allowed-tools`
- "Run with a cheaper/faster model" → `model`
- "Show usage hint" → `argument-hint: "[file] [options]"`

## 4. Where skills live

| Scope | Portable location | Notes |
|---|---|---|
| Global (all projects) | `~/.agents/skills/<name>/` | not in git |
| Project (shared with team) | `<repo>/.agents/skills/<name>/` | commit it |
| Harness-specific | `~/.claude/skills/`, `.claude/skills/`, `~/.config/devin/skills/`, `.devin/skills/`, `~/.codeium/<channel>/skills/`, `.windsurf/skills/` | use only if requested |

Plugin- or package-installed skills may be read-only or overwritten on update — edit a copy instead.

## 5. Writing the description

The description is the only part always in context; it decides whether the skill is ever loaded.

Include:

- **What**: the capability, in one clause.
- **When**: concrete situations, user phrasings, synonyms, file types, tool/system names.
- **Push**: "Use this whenever ..., even if the user doesn't explicitly say ...". Agents under-trigger by default.
- **Boundaries** (if there's a sibling skill that overlaps): "For X use the other-skill instead."

Avoid:

- Vague verbs only ("helps with documents")
- Putting "when to use" guidance in the body — the agent never sees the body until after it decides
- Keyword stuffing that triggers on near-misses

Example:

> Weak: `How to build a dashboard for internal data.`
>
> Strong: `Build fast single-page dashboards for internal company data. Use whenever the user mentions dashboards, KPIs, metrics views, data visualization, or wants to display any team or company data, even if they don't explicitly ask for a "dashboard".`

## 6. Writing the body

Recommended skeleton:

```markdown
# <Title>

<One or two sentences: purpose and the outcome the user gets.>

## Inputs
<What the skill needs; what to ask the user if missing.>

## Workflow
1. ...
2. ...

## Output format
<Template or example.>

## Rules
- <Rule> — <why it matters>

## Bundled files
- `scripts/x.py` — run when ...
- `references/y.md` — read when ...
```

Style:

- Imperative ("Run", "Read", "Ask"), not descriptive ("The agent should consider...").
- Explain the reason behind each rule; reserve ALL-CAPS for true safety boundaries.
- Show output formats with a concrete template or input → output example.
- Stay general. Examples illustrate; they shouldn't become the only case the skill handles.
- Under ~500 lines. Past that, split into `references/` with clear pointers.
- Gate destructive or external side effects (deleting, sending, posting, paying) behind explicit user confirmation.
- Never embed secrets; reference env vars or a secrets manager.

## 7. Bundled resources

- **scripts/**: when every run would otherwise re-derive the same code, or when determinism matters (parsing, validation, file conversion). Scripts can run without being read into context, which saves tokens. Document usage (`python3 scripts/x.py <in> <out>`) and dependencies; prefer the standard library.
- **references/**: domain knowledge, API docs, long checklists, per-variant guides (`aws.md`, `gcp.md`). Add a table of contents to files over ~300 lines.
- **assets/**: templates and static files copied into outputs.

## 8. Audit checklist

- [ ] Frontmatter parses; `name` matches folder; description ≤ 1024 chars, no angle brackets
- [ ] Description covers what + when, with concrete triggers; no heavy overlap with siblings
- [ ] Body has purpose, workflow, output format, rules with reasons
- [ ] Body ≤ ~500 lines; detail in references
- [ ] Every referenced file exists; no orphaned files
- [ ] Scripts run, have usage notes, and list dependencies
- [ ] No overfit instructions tied to one example
- [ ] Destructive/external actions require confirmation
- [ ] No secrets, credentials, or personal data embedded
- [ ] Credentials stored inside the skill folder (e.g. `secrets/`) are documented as never-copy/never-share, with an env-var alternative
- [ ] Tool, API, path, and version references are current

## 9. Minimal templates

### Instruction-only skill

```markdown
---
name: release-notes
description: Draft release notes from merged PRs and commits between two tags. Use whenever the user asks for release notes, a changelog entry, "what shipped", or a summary of changes between versions, even if they don't say "release notes".
---

# Release Notes

Produce user-facing release notes for a version range.

## Workflow
1. Ask for the two tags/refs if not given.
2. Collect commits and merged PRs in range.
3. Group into Features, Fixes, Breaking changes, Internal — skip Internal unless asked.
4. Rewrite each item for end users: what changed and why they'd care.

## Output format
## vX.Y.Z — YYYY-MM-DD
### Features
- ...
### Fixes
- ...
### Breaking changes
- ... (include migration steps)
```

### Skill with a script

```markdown
---
name: csv-profiler
description: Profile CSV files - row counts, column types, nulls, distinct values, outliers. Use whenever the user shares a CSV/TSV and asks what's in it, wants a data-quality check, or needs a quick summary before analysis.
compatibility: Requires python3 (standard library only).
---

# CSV Profiler

Run `python3 scripts/profile.py <file.csv>` and summarize its JSON output for the user.
Highlight columns with >5% nulls or mixed types — those usually break downstream analysis.
```
