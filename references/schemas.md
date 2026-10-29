# File Schemas

Formats for the files the skill-generator workflow reads and writes.

---

## evals/evals.json

Inside the skill folder. Test prompts plus (later) assertions.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "name": "multi-page-invoice",
      "prompt": "Realistic user prompt",
      "expected_output": "Human-readable description of success",
      "files": ["evals/files/invoice.pdf"],
      "expectations": [
        "The output CSV has one row per invoice line item",
        "The total column sums to 1,284.50"
      ]
    }
  ]
}
```

- `id`: unique integer
- `name`: descriptive kebab-case name, used as the eval directory name
- `files`: optional, relative to the skill root
- `expectations`: verifiable statements; start empty, fill in while runs execute

---

## eval_metadata.json

One per eval directory in an iteration: `<workspace>/iteration-N/<eval-name>/eval_metadata.json`. Write it fresh for each iteration that uses new or changed prompts.

```json
{
  "eval_id": 1,
  "eval_name": "multi-page-invoice",
  "prompt": "Realistic user prompt",
  "assertions": ["The output CSV has one row per invoice line item"]
}
```

---

## Run directory

```
<workspace>/iteration-N/<eval-name>/<config>/
├── outputs/
│   ├── <deliverables>
│   ├── transcript.md       steps, tools/commands, errors, final answer
│   ├── user_notes.md       optional: ambiguities and workarounds
│   └── metrics.json        optional
├── timing.json             optional
└── grading.json
```

`<config>` is `with_skill` or `baseline`.

---

## timing.json

Capture as soon as the run finishes if the harness reports it.

```json
{"total_tokens": 84852, "duration_ms": 23332, "total_duration_seconds": 23.3}
```

---

## metrics.json

Optional, written by the executor.

```json
{
  "tool_calls": {"read": 5, "write": 2, "shell": 8},
  "total_tool_calls": 15,
  "files_created": ["filled_form.pdf"],
  "errors_encountered": 0,
  "output_chars": 12450,
  "transcript_chars": 3200
}
```

---

## grading.json

Written by the grader (see `agents/grader.md` for the full example). Required core:

```json
{
  "expectations": [
    {"text": "...", "passed": true, "evidence": "..."}
  ],
  "summary": {"passed": 1, "failed": 0, "total": 1, "pass_rate": 1.0}
}
```

Optional: `execution_metrics`, `timing`, `claims`, `user_notes_summary`, `eval_feedback`. Use the field names `text` / `passed` / `evidence` exactly.

---

## benchmark.md

One per iteration: `<workspace>/iteration-N/benchmark.md`.

```markdown
# Benchmark — <skill-name> — iteration N

Baseline: <none | skill-snapshot | iteration N-1>

| Eval | with_skill pass | baseline pass | Δ | with_skill time | baseline time |
|---|---|---|---|---|---|
| multi-page-invoice | 5/5 (100%) | 2/5 (40%) | +60 | 41s | 30s |
| scanned-receipt    | 3/4 (75%)  | 1/4 (25%) | +50 | 55s | 38s |
| **Overall**        | **89%**    | **33%**   | **+56** | **48s** | **34s** |

## Notes
- <analyst observations from agents/analyzer.md, section 2>
```

If you ran each config several times, report mean ± stddev.

---

## feedback.md

User's review per eval, `<workspace>/iteration-N/feedback.md`. Empty means "looked fine".

```markdown
## multi-page-invoice
the totals row is missing

## scanned-receipt
(no feedback)
```

---

## evals/trigger_evals.json

For description tuning. ~20 items, mixed.

```json
[
  {"query": "realistic, detailed user message", "should_trigger": true, "split": "train"},
  {"query": "near-miss that shares keywords but needs something else", "should_trigger": false, "split": "test"}
]
```

- `split`: `train` (~60%) or `test` (~40%, held out while revising)

Results per description candidate, e.g. in `<workspace>/description-tuning.md`:

```markdown
| Candidate | Train acc | Test acc | False neg | False pos |
|---|---|---|---|---|
| original | 9/12 | 5/8 | 3 | 1 |
| v1       | 11/12 | 7/8 | 1 | 0 |
```

---

## history.md (optional)

Track versions across a long update session at the workspace root.

```markdown
| Version | Parent | Pass rate | Result vs parent | Best |
|---|---|---|---|---|
| v0 (snapshot) | - | 65% | baseline | |
| v1 | v0 | 75% | won | |
| v2 | v1 | 85% | won | yes |
```
