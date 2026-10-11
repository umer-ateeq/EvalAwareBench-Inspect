"""Run the evaluation.

With Inspect's command line (from this folder):
    inspect eval main.py --model openrouter/openai/gpt-oss-20b -T cues=none
    inspect eval main.py --model openrouter/openai/gpt-oss-20b -T cues=F8

Or run both and compare:
    python main.py
"""

from inspect_ai import Task, eval, task

from dataset import make_dataset
from scorer import paper_judge
from solver import make_solver

MODEL = "openrouter/openai/gpt-oss-20b"  # the model we test
JUDGE = "openrouter/openai/gpt-5"        # the model that reads its thinking


@task
def eval_aware(cues: str | list[str] = "none", judge: str = JUDGE):
    """cues: "none", or the cue(s) to switch on, e.g. "F8"."""
    if cues == "none":
        cues_on = []
    elif isinstance(cues, str):
        cues_on = cues.split(",")
    else:
        cues_on = list(cues)

    return Task(
        dataset=make_dataset(cues_on),
        solver=make_solver(),
        scorer=paper_judge(judge),
    )


if __name__ == "__main__":
    for cues in ["none", "F8"]:
        log = eval(eval_aware(cues), model=MODEL)[0]
        print(f"\ncues={cues}: status {log.status}")
        if log.results:
            for score in log.results.scores:
                print(f"  {score.name:15} {score.metrics['mean'].value:.2f}")
