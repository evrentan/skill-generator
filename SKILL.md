---
name: skill-generator
description: Generate new agent skills from scratch and update, refactor, or improve existing skills the user points to. Covers interviewing the user, drafting SKILL.md with bundled scripts/references/assets, auditing an existing skill against best practices, applying targeted edits, running test prompts with and without the skill, grading results, and tuning the description so the skill triggers reliably. Use this whenever the user wants to create, write, scaffold, generate, update, edit, fix, improve, refactor, extend, merge, split, review, or benchmark a skill or SKILL.md, wants to turn a workflow or conversation into a reusable skill, or says a skill is not triggering or not behaving as expected, even if they do not say the word "generator".
license: Apache-2.0. Adapted from Anthropic's skill-creator; see LICENSE
metadata:
  version: "1.1.0"
---

# Skill Generator

Generate new skills and update existing ones, then prove they work.

A skill is a folder with a `SKILL.md` (YAML frontmatter + Markdown instructions) and optional bundled files. It follows the open Agent Skills format, so it should work in any agent harness that reads `.agents/skills/`, `.claude/skills/`, `.devin/skills/`, `.windsurf/skills/`, and similar. Write skills that are portable by default; only use harness-specific features when the user asks for them.

## Pick the mode

Figure out which situation you are in before doing anything else:

| Situation | Mode |
|---|---|
| "Make me a skill for X", "turn this into a skill" | **Create** |
| User gives a path, name, or pasted SKILL.md of an existing skill | **Update** |
| "Why isn't my skill triggering?", "make it trigger better" | **Update → Description tuning** |
| "Is v2 actually better than v1?" | **Update → Evaluate** (with blind comparison) |

If unclear, ask one short question. Then jump in at the right stage — a user who already has a draft does not need the interview again.

Both modes share the same loop:

1. Understand intent
2. Draft or edit
3. Validate structure (`scripts/quick_validate.py`)
4. Run realistic test prompts (optional but recommended)
5. Review results with the user
6. Improve and repeat until the user is happy
7. Tune the description for triggering

Stay flexible. If the user says "skip the tests, just write it", do that. Add these steps to your todo list if you have one, so none get lost.

### Communicating with the user

Users range from senior engineers to people opening a terminal for the first time. Read context cues. "Evaluation" and "benchmark" are usually fine; explain "assertion", "frontmatter", or "JSON" in a few words unless the user clearly knows them.

---

## Create mode

### 1. Capture intent

If the current conversation already contains the workflow (the user says "turn this into a skill"), mine it first: tools used, step order, corrections the user made, input/output formats. Then confirm gaps with the user.

Get answers to:

1. What should the skill let the agent do?
2. When should it trigger? Which phrases or contexts?
3. What does good output look like? Exact format, files, destinations?
4. What tools, MCP servers, CLIs, credentials, or files does it depend on?
5. Any hard rules — things it must never do, approvals it must get first?
6. Should we test it? Skills with objectively checkable output (file transforms, data extraction, code generation, fixed workflows) benefit from test cases. Subjective skills (tone, design) are usually better judged by eye. Suggest a default; let the user decide.

Ask about edge cases, example inputs, and success criteria. Use available docs, MCP servers, or web search to research the domain so you arrive with context instead of making the user explain everything. Don't write test prompts until this is settled.

### 2. Choose name and location

- **Name**: kebab-case, lowercase letters/digits/hyphens, max 64 chars, matches the folder name. Prefer a verb-or-domain name (`pdf-form-filler`, `release-notes`).
- **Location**: ask if not obvious.
  - Global, all projects: `~/.agents/skills/<name>/`
  - Project, shared via git: `<repo>/.agents/skills/<name>/`
  - A harness-specific folder only if the user wants it.

Check that the name doesn't collide with an existing skill in the target location.

### 3. Write the skill

Read `references/skill-format.md` for the full frontmatter and structure reference. The essentials:

**Frontmatter**

- `name` (required)
- `description` (required) — the single most important line. It is the only thing the agent sees when deciding whether to load the skill. Put *what it does* AND *when to use it* here, not in the body. Agents tend to under-trigger skills, so make it a little pushy: list the concrete situations, synonyms, and file types, and say "even if the user doesn't explicitly ask for X". Max 1024 chars, no angle brackets.
- Optional: `license`, `compatibility` (environment requirements), `metadata` (version, author), `allowed-tools`.

**Body** — what the agent should do once the skill is loaded:

- Purpose in one or two sentences
- Step-by-step workflow in imperative form
- Output format, ideally with a template or an example
- Rules and safety constraints, each with the *reason* behind it
- Pointers to bundled files and when to read them

**Bundled resources**

```
skill-name/
├── SKILL.md          required
├── scripts/          deterministic or repetitive work, run rather than read
├── references/       docs loaded only when needed
└── assets/           templates, icons, fonts used in output
```

**Progressive disclosure.** The description is always in context; the body loads on trigger; bundled files load on demand. So keep `SKILL.md` under ~500 lines. If it grows, split detail into `references/` with clear "read X when Y" pointers. Give reference files over ~300 lines a table of contents. When a skill covers several variants (AWS/GCP/Azure, Java/Python), put each in its own reference file so only the relevant one is read.

**Writing style.** Explain *why* instead of shouting MUST/NEVER. Today's models have good judgment; a reason generalizes to cases you didn't foresee, a bare rule doesn't. All-caps rules are a yellow flag — reserve them for true safety boundaries. Keep instructions general rather than overfit to one example. Write a draft, then reread it with fresh eyes as if you were the agent receiving it cold.

**Lack of surprise.** A skill's behavior must match what its description says. Don't create skills containing malware, credential harvesting, data exfiltration, or hidden side effects. Skills that send messages, write to external systems, or delete things should ask for explicit confirmation first.

### 4. Validate

```bash
python3 <this-skill-dir>/scripts/quick_validate.py <path-to-new-skill>
```

Fix errors; consider warnings. Then go to **Testing**, or straight to **Description tuning** if the user skipped tests.

---

## Update mode

The user provides an existing skill (path, name, or pasted content). Your job is to improve it without breaking what already works.

### 1. Locate and read everything

- Resolve the path. If given only a name, look in the usual skill folders (`~/.agents/skills/`, `./.agents/skills/`, `~/.claude/skills/`, `./.devin/skills/`, `~/.config/devin/skills/`, `~/.codeium/*/skills/`, and plugin folders). If several match, ask which one.
- Read `SKILL.md` and every bundled file it references. Note which referenced files are missing and which files exist but are never referenced.
- If the skill is read-only (installed by a plugin or package manager), copy it to a writable location (excluding secrets, see below) and tell the user where the edited copy lives.
- Never open or print files that hold credentials (`secrets/`, `.env`, `*.key`, `*.pem`, `*token*`, `*webhook*`). Note that they exist and how the skill uses them, but don't read their values.

### 2. Snapshot before editing

Copy the original so you can diff, roll back, and benchmark against it. Leave credential files out: a snapshot is a second copy of anything inside the skill, and secrets shouldn't spread to temp or shared folders.

```bash
mkdir -p <workspace>
rsync -a --exclude 'secrets/' --exclude '.env*' --exclude '*.key' --exclude '*.pem' \
  <skill-path>/ <workspace>/skill-snapshot/
```

Use the same exclusions when diffing later (step 6) so the left-out files don't show up as changes. Never edit in place without a snapshot.

**Where `<workspace>` goes:** `<skill-name>-workspace/` somewhere the agent harness does **not** scan for skills, e.g. `${TMPDIR:-/tmp}/skill-generator-workspaces/<skill-name>-workspace/` or a scratch folder in the user's project. Don't put it inside `~/.agents/skills/`, `.claude/skills/`, `.devin/skills/` or similar. The snapshot contains a `SKILL.md` with the same `name`, so a harness may load it as a duplicate skill, and the workspace clutters the user's skill list. Tell the user where it is.

### 3. Understand the requested change

Common requests:

- Add or change a capability, step, or output format
- Fix wrong or outdated behavior ("it keeps doing X")
- Tighten or loosen triggering
- Shrink a bloated skill / split it / merge two skills
- Port a skill to the portable format, or add harness-specific frontmatter
- General "make this better"

If the user only says "improve it", run the audit below and present the findings as a short prioritized list before editing, so they can pick.

### 4. Audit (always do this, even for small changes)

Check the skill against `references/skill-format.md` and this list:

- **Description**: says what AND when? Concrete trigger phrases? Under 1024 chars? Overlaps with sibling skills in the same folder (likely to steal or lose triggers)?
- **Structure**: body under ~500 lines? Detail pushed into references? Broken or orphaned file references?
- **Clarity**: steps imperative and ordered? Output format shown? Ambiguous phrases like "handle appropriately"?
- **Reasons**: rules explain why? Excessive ALL-CAPS?
- **Overfitting**: instructions tied to one example that won't generalize?
- **Repeated work**: anything the agent re-derives every run that should be a bundled script?
- **Safety**: destructive or external side effects gated behind confirmation? No secrets embedded in `SKILL.md`? If credentials live inside the skill folder (e.g. `secrets/`), does the skill say they must never be copied, shared, or committed, and is there an environment-variable alternative?
- **Staleness**: references to tools, APIs, paths, or versions that no longer exist?

### 5. Apply minimal, targeted edits

- Preserve the original `name` and folder name unless the user asks to rename. Renaming breaks anything that invokes the skill by name.
- Preserve the author's voice, structure, and any domain facts you can't verify. Change what the request or audit justifies; don't rewrite for taste.
- Keep frontmatter fields you don't recognize — they're probably harness-specific extensions.
- Bump `metadata.version` if present.
- When removing content, make sure nothing else in the skill depended on it.

### 6. Validate and show the diff

```bash
python3 <this-skill-dir>/scripts/quick_validate.py <skill-path>
diff -ru --exclude secrets --exclude '.env*' --exclude '*.key' --exclude '*.pem' \
  <workspace>/skill-snapshot <skill-path>
```

Summarize what changed and why. For non-trivial changes, offer to run the **Testing** loop with the snapshot as the baseline.

---

## Testing

This section is one continuous sequence; try not to stop partway.

### Write test prompts

Write 2–3 realistic prompts — what a real user would actually type, with file paths, names, casual phrasing, and a bit of backstory. Share them: "Here are a few test cases I'd like to try — do these look right, or want to add any?"

Save to `evals/evals.json` inside the skill folder (schema in `references/schemas.md`). Leave assertions empty for now.

### Workspace layout

Same workspace as the snapshot, outside any folder the harness scans for skills (see Update mode, step 2). In Create mode, also keep the draft outside skill folders until it's final, so the baseline run can't pick it up.

```
<skill-name>-workspace/
├── skill-snapshot/                (update mode only)
└── iteration-1/
    └── <descriptive-eval-name>/
        ├── eval_metadata.json
        ├── with_skill/outputs/
        └── baseline/outputs/
```

Create directories as you go, not upfront. Use descriptive eval names, not `eval-0`.

### Run with and without the skill

For each test prompt run two executions:

- **with_skill**: told to read and follow `<skill-path>/SKILL.md`
- **baseline**:
  - Create mode → no skill at all
  - Update mode → the snapshot (`<workspace>/skill-snapshot/SKILL.md`)

If your harness supports subagents, spawn all runs at once in parallel so they finish together; give each one full context, because subagents can't see your conversation. If it doesn't, do the runs yourself one at a time — less rigorous, since you know the skill, but still a useful check; skip the baseline in that case.

**Check permissions before spawning.** In many harnesses, background or non-interactive subagents can't ask the user for approval, so any tool that needs it gets silently denied. Usually that means shell commands and file writes. A skill whose core steps run commands then gets tested without its core steps, and both configurations fall back to the same improvised workarounds. The results look plausible but measure nothing. So, before launching:

1. List the tools the skill's main path needs (shell, file writes, network, MCP).
2. If any of them need approval in this harness, pick one:
   - **Foreground runs, one at a time**, so the user can approve prompts. Tell them roughly how many prompts to expect.
   - **Pre-approval**: ask the user to allow those specific commands for the session or the workspace folder first. Don't change permission settings yourself.
   - **Read-only skills**: if only file writes are blocked, have executors return the deliverables in their final message and save them yourself.
3. Ask the user which one they prefer when it isn't obvious.

After the **first** run finishes, check its transcript for denied tools before waiting for the rest. If its core steps were blocked, stop, tell the user, and fix the setup, rather than grading runs that couldn't do the task.

Prompt template for an executor:

```
Execute this task as a user would expect.
- Skill: <path to SKILL.md, or "none — do not load any skill named <skill-name>">
- Task: <eval prompt>
- Input files: <paths or "none">
- Save all deliverables to: <run-dir>/outputs/
- Also write <run-dir>/outputs/transcript.md: the steps you took, tools/commands used, errors hit, and your final answer.
- If anything was ambiguous or you used a workaround, note it in <run-dir>/outputs/user_notes.md.
- Do not perform irreversible actions or contact external systems; simulate them and record what you would have done.
```

Caution for the baseline: if the draft skill is already installed in a folder the harness scans, the baseline agent may load it anyway. Explicitly tell it not to, or keep the draft outside skill folders until it's final.

If the harness reports tokens or duration when a run finishes, save them immediately to `<run-dir>/timing.json` — that data is often not recoverable later.

### Draft assertions while runs execute

Use the waiting time to write objectively verifiable assertions with descriptive names for each eval, then explain them to the user. Good assertions are *discriminating*: they pass when the skill truly succeeds and fail when it doesn't (check content, not just that a file exists). Don't force assertions onto subjective qualities — leave those to human review. Write them into `eval_metadata.json` and `evals/evals.json`.

### Grade and summarize

1. Grade each run per `agents/grader.md` (spawn a grader subagent or do it inline). Save `grading.json` next to `outputs/`. Where an assertion can be checked by a script, write and run one instead of eyeballing.
2. Write `iteration-N/benchmark.md`: a table per eval with pass rate for with_skill vs baseline, plus time/tokens if captured, and the overall delta. Format in `references/schemas.md`.
3. Do an analyst pass per the "Analyzing benchmark results" section of `agents/analyzer.md`: assertions that pass in both configs (not discriminating), always fail (broken), high variance (flaky), time/token cost.
4. If any run hit denied tools, missing access, or other harness problems, put a **Confound** note at the top of `benchmark.md` saying what was blocked and which assertions it affects. Tell the user before presenting the numbers, so a harness failure isn't mistaken for a skill failure or success.

### Review with the user — before you start fixing things

Get results in front of the user before you revise anything. For each eval show the prompt, the with_skill output (inline, or the file path for binaries like .docx/.xlsx), the baseline output for contrast, and the grades. Then the benchmark table. Ask for feedback per eval; empty feedback means it looked fine. Save their feedback to `iteration-N/feedback.md`.

---

## Improving the skill

This is the heart of the loop.

1. **Generalize from feedback.** The skill will run on far more prompts than these few test cases. Don't add fiddly, overfit patches or oppressive MUSTs. For a stubborn issue, try a different framing, metaphor, or recommended working pattern.
2. **Keep it lean.** Read the transcripts, not just outputs. If the skill makes the agent waste time on unproductive steps, remove the instructions causing it.
3. **Explain the why.** Even if feedback is terse, figure out what the user really needs and encode that understanding, not just the literal complaint.
4. **Bundle repeated work.** If every run independently wrote the same helper script or took the same multi-step detour, put that script in `scripts/` and tell the skill to use it.

Draft the revision, reread it fresh, then improve it again.

### Iterate

1. Apply improvements
2. Re-run all evals into `iteration-<N+1>/`, including baselines (create mode: still no-skill; update mode: snapshot or previous iteration — your call)
3. Show results alongside the previous iteration's
4. Collect feedback, improve, repeat

Stop when the user is happy, feedback is empty, or you're no longer making meaningful progress.

### Blind comparison (optional)

When the user wants rigor ("is the new version really better?"), give both outputs to an independent agent labeled A/B without saying which is which — follow `agents/comparator.md`. Then unblind and explain why the winner won with `agents/analyzer.md`. Requires subagents; skip otherwise.

---

## Description tuning

The description decides whether the skill ever gets used. Offer this after creating or substantially updating a skill, or whenever the user reports triggering problems.

### How triggering works

The agent sees each skill's name + description in a list and decides whether to load one. Agents generally only consult skills for tasks they can't trivially do themselves — "read this file" won't trigger anything regardless of the description. So trigger tests must be substantive, multi-step requests.

### 1. Build a trigger eval set

Write ~20 queries, saved as `evals/trigger_evals.json` (schema in `references/schemas.md`):

- **8–10 should-trigger**: different phrasings of the same intent, formal and casual, some that never name the skill or file type, uncommon use cases, and cases where this skill competes with a sibling skill and should win.
- **8–10 should-not-trigger**: near-misses only — shared keywords but a different need, adjacent domains, cases where another skill or plain tools are the better choice. "Write a fibonacci function" as a negative for a PDF skill tests nothing.

Make them realistic: file paths, company names, column names, typos, lowercase, backstory, varied length.

Bad: `"Format this data"`. Good: `"ok so my boss sent me 'Q4 sales final FINAL v2.xlsx' (in downloads) and wants a profit margin % column, revenue is col C and costs col D i think"`.

Show the set to the user and let them edit it before running. Bad evals produce bad descriptions.

### 2. Measure

Run each query against a fresh agent that sees the candidate description among the real list of other installed skills (names + descriptions), and record whether it chooses this skill. Options, best first:

- The harness's non-interactive mode with the skill installed, checking whether the skill was invoked
- A subagent given the full skills list (names + descriptions) and the query, asked which skill(s) it would load — a reasonable approximation
- Doing it yourself — weakest, because you're biased by knowing the target

Run each query ~3 times if feasible; triggering is noisy. Hold out ~40% of queries as a test set and don't look at them while revising, to avoid overfitting.

### 3. Revise and re-measure

Look at misses on the training split: false negatives usually mean missing trigger contexts or synonyms; false positives usually mean the description is too broad or overlaps a sibling. Rewrite, re-measure on both splits, up to ~5 rounds. Pick the version with the best **held-out** score.

### 4. Apply

Update the frontmatter, show the user before/after and the scores, and re-run `quick_validate.py`.

---

## Finishing up

- Run `scripts/quick_validate.py` one last time.
- Delete or keep the `<skill-name>-workspace/` — ask the user; don't silently delete it.
- Summarize: skill path, what it does, how to invoke it, test results, and any known limitations.
- If the user wants a shareable package, leave credentials and workspaces out: `cd <parent-dir> && zip -r <skill-name>.zip <skill-name> -x '*-workspace/*' '*/secrets/*' '*.env*' '*.key' '*.pem'`. Then list the zip contents (`unzip -l`) to confirm nothing sensitive went in.

## Bundled files

- `references/skill-format.md` — frontmatter fields, structure, portability notes, description patterns. Read when writing or auditing a skill.
- `references/schemas.md` — `evals.json`, `eval_metadata.json`, `grading.json`, `benchmark.md`, `trigger_evals.json`. Read before writing any of those files.
- `agents/grader.md` — how to grade assertions against outputs.
- `agents/comparator.md` — blind A/B comparison.
- `agents/analyzer.md` — why one version won, and benchmark pattern analysis.
- `scripts/quick_validate.py` — structural validation of a skill folder.

The core loop one more time: understand → draft/edit → validate → test with and without → review with the user → improve → repeat → tune the description.
