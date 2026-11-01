# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-10-31

### Added

- **Create** mode: interview the user or mine the current conversation, then
  draft `SKILL.md` with bundled scripts, references and assets.
- **Update** mode: snapshot the original, audit it against best practices,
  apply minimal targeted edits and show a diff.
- Test loop that runs realistic prompts with and without the skill and grades
  the results (`agents/grader.md`).
- Blind A/B comparison and win analysis (`agents/comparator.md`,
  `agents/analyzer.md`).
- Description tuning with train/held-out trigger evals.
- `scripts/quick_validate.py`: stdlib-only structural validator for
  frontmatter, naming, description quality, body size, file references and
  credential-like files.
- `references/skill-format.md` and `references/schemas.md`.
- Plugin manifests for Devin, Claude Code, Codex and Cursor, with the skill
  under `skills/skill-generator/`.
- Project logo, used in the README and the Codex and Cursor plugin cards.
- Contributing guide, security policy, issue and pull request templates,
  Dependabot and a CI workflow that validates the skill, checks the license
  copy stays in sync and verifies the manifest versions match on Linux,
  macOS and Windows.

[Unreleased]: https://github.com/evrentan/skill-generator/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/evrentan/skill-generator/releases/tag/v1.0.0
