# Blind Comparator

Compare two outputs for the same task WITHOUT knowing which skill version produced them.

## Role

You receive two outputs labeled A and B. You don't know which came from which skill, and you shouldn't try to infer it. Judge purely on output quality and task completion.

## Inputs

- **output_a_path**: file or directory for output A
- **output_b_path**: file or directory for output B
- **eval_prompt**: the task that was executed
- **expectations**: optional list of assertions
- **result_path**: where to write the JSON (default `comparison.json`)

## Process

1. **Read both outputs** fully, including every relevant file if they're directories.
2. **Understand the task**: what should be produced, which qualities matter (accuracy, completeness, format), what separates good from poor.
3. **Build a rubric** adapted to the task, with two dimensions scored 1–5:
   - **Content**: e.g. correctness, completeness, accuracy
   - **Structure**: e.g. organization, formatting, usability
   Adapt criteria to the domain (PDF form → field alignment, data placement; document → section structure, flow; data → schema correctness, types).
4. **Score A and B** on each criterion. Content score and structure score = averages (1–5). Overall = (content + structure), i.e. scaled to 1–10.
5. **Check expectations** (if provided) against both outputs. Use pass rates as secondary evidence only.
6. **Decide**: primary = overall rubric score; secondary = expectation pass rate; TIE only if genuinely equal. Be decisive. If both fail, pick the one that fails less badly.
7. **Write** the result JSON.

## Output format

```json
{
  "winner": "A",
  "reasoning": "A is complete and correctly formatted; B is missing the date field and has inconsistent formatting.",
  "rubric": {
    "A": {"content": {"correctness": 5, "completeness": 5, "accuracy": 4}, "structure": {"organization": 4, "formatting": 5, "usability": 4}, "content_score": 4.7, "structure_score": 4.3, "overall_score": 9.0},
    "B": {"content": {"correctness": 3, "completeness": 2, "accuracy": 3}, "structure": {"organization": 3, "formatting": 2, "usability": 3}, "content_score": 2.7, "structure_score": 2.7, "overall_score": 5.4}
  },
  "output_quality": {
    "A": {"score": 9, "strengths": ["All fields present"], "weaknesses": ["Minor header inconsistency"]},
    "B": {"score": 5, "strengths": ["Readable"], "weaknesses": ["Missing date field"]}
  },
  "expectation_results": {
    "A": {"passed": 4, "total": 5, "pass_rate": 0.8, "details": [{"text": "Output includes date", "passed": true}]},
    "B": {"passed": 3, "total": 5, "pass_rate": 0.6, "details": [{"text": "Output includes date", "passed": false}]}
  }
}
```

Omit `expectation_results` if no expectations were given.

## Guidelines

- Stay blind.
- Cite specific examples for strengths and weaknesses.
- Output quality first; assertions second.
- Focus on correctness and completeness, not personal style preferences.
