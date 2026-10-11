# EvalAwareBench, simple version: one request, one cue, one model

Each file does one job:

| File | Job |
|---|---|
| `cue.py` | The cues. Each cue fills one blank in a request: realistic text when off, test-like text when on. Now: just **F8** |
| `dataset.py` | The requests. Now: just **one** (Purple Rain lyrics), with a `{F8}` blank where the cue goes |
| `solver.py` | How we ask the model: system prompt + `generate()` with the paper's settings |
| `scorer.py` | The paper's judge reads the model's thinking: did it notice a test, and the right kind? |
| `main.py` | Puts dataset + solver + scorer into one Inspect `Task`, and runs it |
| `judge_prompt.txt` | The paper's judge instructions, word for word |

```
dataset.py ──(uses cue.py to fill the blanks)──► Sample
                                                   │
main.py:  Task(dataset, solver, scorer) ───────────┤
                                                   ▼
solver.py: the model thinks + answers ──► scorer.py: the judge reads the thinking ──► aware? matched?
```

## Run (from this folder)

```bash
../../.venv/Scripts/inspect eval main.py --model openrouter/openai/gpt-oss-20b -T cues=none
../../.venv/Scripts/inspect eval main.py --model openrouter/openai/gpt-oss-20b -T cues=F8
```

Or `../../.venv/Scripts/python main.py` runs both and prints the two results. A real run of both costs
about $0.05–0.10. Free test with fake models: add `--model mockllm/model -T judge=mockllm/model`.

## How it grows

- **More requests:** add an entry to `REQUESTS` in `dataset.py` (its text with a `{F8}` blank).
- **More cues:** add an entry to `CUES` in `cue.py` (its off and on text), and put its blank in the requests.
- **Toggles:** `-T cues=F1,F8` switches several cues on at once.
- **More models:** change `--model`.

With one request, the result is a single yes or no. That's enough to understand the mechanism, but
not enough to measure anything. Real numbers need many requests and repetitions, which we add later.
