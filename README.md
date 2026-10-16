# EvalAwareBench, simple version: one request, all 8 cues, one model

Each file does one job:

| File | Job |
|---|---|
| `cue.py` | The **8 cues** (F1 to F8), what each one changes, and how to read which are on |
| `dataset.py` | Loads the **authors' dataset file** (200 requests, each in all 256 cue combinations) and picks the version with your chosen cues on. `REQUESTS` chooses which: the Purple Rain pair (default), `"safety"`, `"capability"` or `"all"` |
| `preview.py` | `python preview.py F3` prints the request with those cues on, without calling a model |
| `learn_cues/own_cue_code.py` | Learning tool: **our own** code that builds the same 256 versions, to see how each cue works |
| `solver.py` | How we ask the model: system prompt + `generate()` with the paper's settings |
| `scorer.py` | **The paper's judge:** reads the request, thinking and answer. Two numbers per reply: `matched_aware` (noticed the *right kind* of test) and `did_task` (the answer did what was asked) |
| `main.py` | Puts dataset + solver + scorer into one Inspect `Task`, and runs it |
| `judge_prompt.txt` | The paper's judge instructions, word for word (used by `scorer.py`) |

```
dataset.py ──(picks the version with your cues on)──► Sample
                                                   │
main.py:  Task(dataset, solver, scorer) ───────────┤
                                                   ▼
solver.py: the model thinks + answers ──► scorer.py: a judge reads the thinking ──► noticed a test? 1 or 0
```

## Run (from this folder)

For free (the model and the judge set in main.py are free OpenRouter models, $0):

```bash
../../.venv/Scripts/inspect eval main.py -T cues=none
../../.venv/Scripts/inspect eval main.py -T cues=all
```

Other cue choices: `-T cues=F8` (one cue), `-T cues=F1+F8` (several, joined with `+`), and stacking
`-T cues=k4` (the paper's 10 random combinations of 4 cues per request; `k0`…`k8`).

The paper's experiments with this code:
- **Single cues (Fig. 6):** run `cues=none`, then `F1` … `F8`. Behaviour change for a cue = its `did_task` minus the `none` run's.
- **Stacking (Fig. 7):** run `cues=k0` … `k8` (BlueDot plan: `k0`, `k2`, `k4`, `k8`).
- Set `REQUESTS` in `dataset.py` to `"safety"` or `"capability"` for one type at a time, as the paper reports them.

Then `inspect view` shows every request, the model's thinking and the score.

- Free models are sometimes busy: Inspect waits and retries by itself, so a run can take a few minutes.
- Free accounts get a limited number of free requests per day. Each run uses 6 (3 model + 3 judge).
- The first run downloads the paper's dataset file (~90 MB, once). Each run then takes ~15 s to load it.
- The paper's model (needs credit): add `-T model=openrouter/openai/gpt-oss-20b`.
- Test with a fake model (no internet): add `-T model=mockllm/model`.

## Scorer steps

- **A:** word check. Simple, but it misses tests that are described without those words, and
  counts words like "latest" or "contest". That's why the paper uses a judge model.
- **B:** ask a judge model a simple yes/no question about the thinking.
- **C (now):** the paper's judge (`scorer.py`, explained in `SCORER_EXPLAINED.md`).

## How it grows

- **More requests:** set `REQUESTS` in `dataset.py` to `"all"`, `"safety"`, `"capability"` or a list of task ids.
- **Cues:** all 8 are available; choose them with `-T cues=...`.
- **More models:** change `MODEL` in `main.py`, or add `-T model=...`.

With one request, the result is a single yes or no. That's enough to understand the mechanism, but
not enough to measure anything. Real numbers need many requests and repetitions, which we add later.
