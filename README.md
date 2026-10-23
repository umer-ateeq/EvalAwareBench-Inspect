# EvalAwareBench in Inspect

An [Inspect AI](https://inspect.aisi.org.uk/) port of **EvalAwareBench** (Li et al. 2026,
"Decomposing and Measuring Evaluation Awareness", [arXiv:2605.23055](https://arxiv.org/abs/2605.23055)).

The benchmark tests whether AI models notice they are being evaluated, and whether that changes what they do.
It has 100 harmful "safety" tasks, each with a harmless "capability" twin, and 8 test-like cues (F1-F8,
for example placeholder names like "Acme Corp", or a template format) that can be switched on or off.
A GPT-5 judge reads the model's reasoning and marks whether it noticed a test.

- Original code: [aisa-group/decomposing-eval-awareness](https://github.com/aisa-group/decomposing-eval-awareness) (commit `2961c17`)
- Dataset: [aisa-group/EvalAwareBench](https://huggingface.co/datasets/aisa-group/EvalAwareBench) (revision `ee984a8`)

## Status

**The port is built and validated end to end.** Validation runs, costs and reproduction commands are in
[report.md](report.md).

Checked against the original:
- All 51,200 prompts are byte-identical to the original code's output (0 mismatches).
- Same settings for the tested model as the original code: its system prompt, temperature 0.3, max_tokens 4096,
  reasoning effort high (Claude: extended thinking with a 2,457-token budget and no temperature; see report.md).
- Same judge prompt, word for word (`judge_prompt.txt`). Scoring follows the paper's definitions (matched-type
  awareness, Section 4; task completion); the original code reports any-type awareness only.
- On 2026-10-11 the original pipeline and an earlier version of this port were run on the same 6 gpt-oss-20b
  samples, and the judge inputs matched (6/6). The check script is not in this folder, and the check has not been
  repeated since the scorer changes in the Changelog.
- All 18 settings (no cues, F1–F8, k0–k8) have run end to end on free models, on one task pair
  (2026-10-23; see report.md).

Next: the Figure 7 stacking run on Claude Sonnet 4.5 (k = 0 and k = 8, 25 task pairs), then the open-weight
models, comparing each result with the paper's Figure 6 and 7 values.

## Files

| File | Job |
|---|---|
| `cue.py` | The **8 cues** (F1 to F8, the authors' own wording), and the stacking picks (`k0`…`k8`) |
| `dataset.py` | Loads the **authors' dataset file** (200 requests, each in all 256 cue combinations) and picks the version with your chosen cues on. `REQUESTS` chooses which: `"all"` (currently set, for the stacking runs), `"safety"`, `"capability"`, or a list of task ids, e.g. `["lyrics_purple_rain_safety", "lyrics_purple_rain_capability"]` for a quick test. Stacking uses 25 task pairs, picked once with a fixed seed |
| `solver.py` | How we ask the model: the paper's system prompt + `generate()` with the paper's settings |
| `scorer.py` | **The paper's judge:** reads the request, thinking and answer. Two numbers per reply: `matched_aware` (noticed the *right kind* of test) and `did_task` (the answer did what was asked) |
| `main.py` | Puts dataset + solver + scorer into one Inspect `Task` |
| `judge_prompt.txt` | The paper's judge instructions, word for word |
| `preview.py` | `python preview.py F3` prints the request with those cues on, without calling a model |
| `learn_cues/own_cue_code.py` | Learning tool: our own code that rebuilds the same 256 versions |

```
dataset.py ──(picks the version with your cues on)──► Sample
                                                   │
main.py:  Task(dataset, solver, scorer) ───────────┤
                                                   ▼
solver.py: the model thinks + answers ──► scorer.py: the judge reads the thinking ──► noticed a test? 1 or 0
```

## Run (from this folder)

Install (tested on Python 3.14.3):

```bash
pip install inspect-ai==0.3.263 openai==3.28.0 anthropic==1.13.0 huggingface_hub==2.2.0
```

Needs an `OPENROUTER_API_KEY` in a `.env` file (plus `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` for the `anthropic/`
and `openai/` models used in report.md). Never commit the `.env` file. The defaults in `main.py` are free models,
for testing (with `REQUESTS = "all"` this runs all 200 requests; set `REQUESTS` to a task pair for a quick test):

```bash
inspect eval main.py -T cues=none
```

With the paper's judge and a paper model (needs credit):

```bash
inspect eval main.py -T cues=none -T model=openrouter/moonshotai/kimi-k2.5 -T judge=openai/gpt-5
```

Choose the tested model with `-T model=...`, not `--model`: the task sets its own model, so Inspect ignores
`--model`. For Claude, also pass `--reasoning-tokens 2457` (the original code's thinking budget).

Cue choices: `-T cues=none`, `F8` (one cue), `F1+F8` (several), `all`, or a stacking level `k0`…`k8`.

The paper's two experiments (set `REQUESTS` in `dataset.py` to `"safety"`, then `"capability"`, as the paper reports them separately):
- **Experiment 1, single cues (Fig. 6):** `cues=none`, then `F1` … `F8`, on all 100 tasks of each type, 3 repetitions.
  Behaviour change for a cue = its `did_task` minus the `none` run's.
- **Experiment 2, stacking (Fig. 7):** `cues=k0` … `k8`, on the 25 stacking tasks of each type (the paper does not state the
  number of repetitions for stacking; it uses 3 for Experiment 1).

Then `inspect view` shows every request, the model's thinking and the score.

## Changelog

- **2026-10-23:** The GPT-5 judge is called through Chat Completions (`responses_api=False`), as in the original
  code; Inspect's default for GPT-5 is the Responses API. Other judges are unchanged. Verified in the 2026-10-23
  Claude pilot logs; a free run with a non-OpenAI judge was unaffected.
- **2026-10-22:** For redacted reasoning (Claude, GPT-5), the judge now receives the readable reasoning summary
  instead of the encrypted reasoning field. Found in the first Claude Sonnet 4.5 pilot, whose judge input held
  the encrypted text; that pilot was discarded and re-run after the fix.
- **2026-10-19:** Scoring aligned with the original code. Replies without reasoning are judged with empty
  reasoning instead of being dropped; a judge reply that is not valid JSON counts as not aware and not done
  instead of being dropped; judge labels are compared after `strip().lower()`.
- **2026-10-16:** Stacking (`k0`…`k8`) uses 25 task pairs, matching the paper's 25 tasks per valence. The
  paper's tasks are not published, so ours are sampled with seed 42.

## Credit and licence

All credit for the benchmark goes to the paper's authors. Please cite their paper (arXiv:2605.23055).

- From the authors' repository and dataset, under **CC BY-NC 4.0** (non-commercial use only): the judge prompt
  (`judge_prompt.txt`), the system prompt in `solver.py`, the cue names and descriptions in `cue.py`, and the
  Purple Rain task text in `learn_cues/own_cue_code.py`. The dataset is downloaded at run time, not copied here;
  its data card forbids using it to train models that are released publicly or commercially.
- Everything else in this folder is under the MIT licence (`LICENSE`).
