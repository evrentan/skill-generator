# Contributing to skill-generator

Thanks for helping. Bug reports, better instructions, new validator checks
and sharper audit rules are all welcome.

## Ground rules

- **Portable by default.** The skill follows the open Agent Skills format and
  must keep working in any harness that reads skills from folders
  (`.agents/skills/`, `.claude/skills/`, `.devin/skills/`, ...). Put
  harness-specific behaviour behind a clear "if your harness supports it"
  note.
- **Standard library only** in `scripts/`. PyYAML may be used when it is
  installed, but the fallback parser must keep working without it.
- **Never touch credentials.** The skill must never read, copy or package
  `secrets/`, `.env*`, `*.key` or `*.pem` files. Do not weaken that rule.
- **No real data.** Never commit hostnames, tokens, company names, customer
  data or private skills. Use `example.com` and `<token>` placeholders, and
  redact anything you paste into issues too.
- **Cross-platform.** Scripts must run on Linux, macOS and Windows with
  Python 3.11+.
- **Security issues** go through private reporting, not public issues. See
  [`SECURITY.md`](SECURITY.md).

## Development setup

```bash
git clone https://github.com/evrentan/skill-generator.git
cd skill-generator
```

To try your changes in an agent, symlink the checkout into a skills folder:

```bash
ln -s "$PWD/skills/skill-generator" ~/.agents/skills/skill-generator
```

## Making a change

- The skill lives in `skills/skill-generator/`. Keep `SKILL.md` under 500
  lines. Move detail into `references/` or `agents/` and link it from
  `SKILL.md`.
- Every file in `references/`, `agents/` and `scripts/` must be referenced
  from `skills/skill-generator/SKILL.md`; the validator warns about orphans.
- If you change behaviour, update `skills/skill-generator/SKILL.md`, the
  matching `references/` or `agents/` docs, and the README.
- If you change the license, edit the root `LICENSE` and copy it to
  `skills/skill-generator/LICENSE`; CI checks they stay in sync.
- Bump `metadata.version` in `skills/skill-generator/SKILL.md` and the
  `version` fields in `plugin.json`, `.claude-plugin/plugin.json`,
  `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json` and
  `.cursor-plugin/marketplace.json` together when you cut a release; CI
  checks they match.
- For changes to the instructions, run a few test prompts with and without
  your change (the skill's own Evaluate mode works well) and summarise the
  results in the pull request.

## Checks before a pull request

CI runs these on Linux, macOS and Windows. Run them locally first:

```bash
python skills/skill-generator/scripts/quick_validate.py skills/skill-generator
python -m py_compile skills/skill-generator/scripts/quick_validate.py tools/check_release.py
python tools/check_release.py
```

## Pull requests

- Keep each pull request focused on one change.
- Describe what changed and why, and how you tested it.
- Add an entry under `## [Unreleased]` in [`CHANGELOG.md`](CHANGELOG.md).
- New dependencies, including GitHub Actions, must be pinned (actions to a
  full commit SHA) and released at least 7 days earlier.

By contributing, you agree that your contributions are licensed under the
Apache License 2.0.
