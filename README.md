# skill-generator

An agent skill that creates new skills and updates, refactors, or improves existing ones, then proves they work by testing them with and without the skill.

It follows the open Agent Skills format (a folder with a `SKILL.md` plus optional bundled files), so it works in any agent harness that reads skills from folders such as `.agents/skills/`, `.claude/skills/`, `.devin/skills/`, or `.windsurf/skills/`.

## What it does

| You say | Mode |
|---|---|
| "Make me a skill for X", "turn this workflow into a skill" | **Create** |
| "Update / fix / improve this skill" (path, name, or pasted `SKILL.md`) | **Update** |
| "Why isn't my skill triggering?" | **Description tuning** |
| "Is v2 actually better than v1?" | **Evaluate** (blind A/B comparison) |

Both modes share one loop:

1. Understand intent (interview, or mine the current conversation)
2. Draft or edit `SKILL.md` and bundled files
3. Validate structure with `scripts/quick_validate.py`
4. Run realistic test prompts with and without the skill
5. Grade and review results with the user
6. Improve and repeat
7. Tune the description so the skill triggers reliably

Update mode always snapshots the original first, audits it against best practices, applies minimal targeted edits, and shows a diff. Credential files (`secrets/`, `.env*`, `*.key`, `*.pem`) are never read, copied, or packaged.

## Installation

Clone the repo into a folder your agent harness scans for skills. The folder name must stay `skill-generator`.

```bash
# Global, available in all projects
git clone https://github.com/evrentan/skill-generator.git ~/.agents/skills/skill-generator

# Or per project, shared via git
git clone https://github.com/evrentan/skill-generator.git .agents/skills/skill-generator
```

If you keep the clone elsewhere, symlink it instead:

```bash
ln -s /path/to/skill-generator ~/.agents/skills/skill-generator
```

## Usage

Just ask your agent in plain language; the skill triggers on requests to create, write, scaffold, update, fix, improve, refactor, merge, split, review, or benchmark a skill:

- "Turn what we just did into a reusable skill."
- "My `release-notes` skill keeps skipping the changelog step, can you fix it?"
- "My pdf skill never triggers, tune the description."

### Validator

The bundled validator checks any skill folder for frontmatter errors, naming rules, description length and quality, body size, broken or orphaned file references, and credential-like files. It uses only the Python standard library (PyYAML is used if installed).

```bash
python3 scripts/quick_validate.py <path-to-skill>
```

Errors exit with code 1; warnings are informational.

## Repository layout

```
skill-generator/
├── SKILL.md                  skill instructions (entry point)
├── agents/
│   ├── grader.md             grade assertions against run outputs
│   ├── comparator.md         blind A/B comparison of two outputs
│   └── analyzer.md           explain why a version won; benchmark patterns
├── references/
│   ├── skill-format.md       frontmatter, structure, portability, audit checklist
│   └── schemas.md            evals.json, grading.json, benchmark.md, trigger_evals.json
└── scripts/
    └── quick_validate.py     structural validation of a skill folder
```

## License

Apache License 2.0, see [LICENSE](LICENSE). Adapted from Anthropic's [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) skill.
