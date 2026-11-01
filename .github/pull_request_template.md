## What and why

<!-- What does this change, and why is it needed? Link related issues. -->

## How I tested it

<!-- Validator output, test prompts you ran with and without the change, agents you tried (redacted). -->

## Checklist

- [ ] Instructions stay portable across agent harnesses
- [ ] Scripts use only the Python standard library (PyYAML optional)
- [ ] No real hostnames, tokens, company names, customer data or private skills
- [ ] Credential files are still never read, copied or packaged
- [ ] `python skills/skill-generator/scripts/quick_validate.py skills/skill-generator` passes and `SKILL.md` stays under 500 lines
- [ ] Docs (`SKILL.md`, `references/`, `agents/`, README) and `CHANGELOG.md` updated
