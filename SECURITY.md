# Security

skill-generator writes and edits skill files and runs test prompts in your
agent. It never reads, copies or packages credential files (`secrets/`,
`.env*`, `*.key`, `*.pem`), and the bundled validator flags them.

- Never commit secrets or private skills. See `.gitignore`.
- Report vulnerabilities with GitHub private vulnerability reporting:
  https://github.com/evrentan/skill-generator/security/advisories/new
  Please do not open public issues for vulnerabilities.
- Supported versions: the latest release.
- Review skills generated or edited by any tool, including this one, before
  you install them: a skill's instructions and scripts run with your agent's
  permissions.
