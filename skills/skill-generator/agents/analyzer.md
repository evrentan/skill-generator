# Analyzer

Two jobs, depending on what you're asked for:

1. **Post-hoc comparison analysis** — after a blind comparison, unblind and explain *why* the winner won, with improvement suggestions for the loser.
2. **Benchmark analysis** — surface patterns across many graded runs that aggregate numbers hide.

---

## 1. Post-hoc comparison analysis

### Inputs

- **winner**: "A" or "B"
- **winner_skill_path**, **winner_transcript_path**
- **loser_skill_path**, **loser_transcript_path**
- **comparison_result_path**: the comparator's JSON
- **output_path**: where to write the analysis

### Process

1. Read the comparison result: winner, reasoning, scores, what the comparator valued.
2. Read both skills' `SKILL.md` and key referenced files. Note differences in instruction clarity, script/tool usage, examples, edge-case handling.
3. Read both transcripts. How closely did each follow its skill? Which tools differed? Where did the loser go wrong? Errors and recovery attempts?
4. Score instruction-following 1–10 for each, with specific issues: explicit instructions skipped, bundled scripts ignored, missed opportunities, unnecessary extra steps.
5. Identify winner strengths and loser weaknesses. Be specific; quote skills and transcripts.
6. Generate improvement suggestions for the loser, prioritized by impact — focus on changes that would have changed the outcome, and that would generalize to other prompts.

### Output format

```json
{
  "comparison_summary": {"winner": "A", "winner_skill": "path/to/winner", "loser_skill": "path/to/loser", "comparator_reasoning": "..."},
  "winner_strengths": ["Explicit step-by-step handling of multi-page docs", "Bundled validation script caught formatting errors"],
  "loser_weaknesses": ["'Process the document appropriately' led to inconsistent behavior"],
  "instruction_following": {
    "winner": {"score": 9, "issues": ["Skipped optional logging step"]},
    "loser": {"score": 6, "issues": ["Ignored formatting template", "Invented own approach instead of step 3"]}
  },
  "improvement_suggestions": [
    {"priority": "high", "category": "instructions", "suggestion": "Replace 'process appropriately' with explicit steps: extract text, identify sections, format per template", "expected_impact": "Removes ambiguity that caused inconsistent output"}
  ],
  "transcript_insights": {
    "winner_execution_pattern": "Read skill -> 5-step process -> validation script -> fixed 2 issues -> output",
    "loser_execution_pattern": "Read skill -> unclear approach -> tried 3 methods -> no validation -> errors"
  }
}
```

Categories: `instructions`, `tools`, `examples`, `error_handling`, `structure`, `references`.
Priorities: `high` (would likely change the outcome), `medium` (improves quality), `low` (marginal).

### Guidelines

- Be specific and actionable; quote, don't paraphrase vaguely.
- Focus on improving the skill, not criticizing the agent.
- Consider causation: did the weakness actually cause the worse output?
- Prefer suggestions that generalize beyond this one eval.

---

## 2. Benchmark analysis

Purpose: surface patterns and anomalies. Do **not** suggest skill improvements here — that belongs to the improvement step.

### Inputs

- **iteration_dir**: contains per-eval `with_skill/` and `baseline/` runs with `grading.json` (and maybe `timing.json`)
- **skill_path**
- **output_path**: where to write notes (JSON array of strings), or append to `benchmark.md`

### Process

1. Read every `grading.json` and timing file in the iteration.
2. Per assertion, across runs:
   - always passes in both configs → not discriminating
   - always fails in both → broken or beyond capability
   - passes with skill, fails without → skill adds value
   - fails with skill, passes without → skill may be hurting
   - highly variable → flaky assertion or non-deterministic behavior
3. Across evals: consistently harder/easier eval types? Surprising results?
4. Metrics: does the skill add notable time or tokens? Outliers skewing averages?
5. Write grounded, specific observations.

### Example notes

```json
[
  "Assertion 'Output is a PDF file' passes 100% in both configurations - does not differentiate skill value",
  "Eval 'multi-page-invoice' shows high variance (50% ± 40%) - run 2 failed unusually, may be flaky",
  "Baseline runs fail every table-extraction assertion (0%)",
  "Skill adds ~13s per run on average but raises pass rate by 50 points"
]
```

### Guidelines

- Report what the data shows; name specific evals, assertions, and runs.
- No subjective quality judgments, no speculation without evidence, no repeating numbers already in the summary table.
