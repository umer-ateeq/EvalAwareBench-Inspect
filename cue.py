"""The 8 cues from the paper. Each one makes a request look more like a test.

The authors wrote every request in all 256 on/off combinations of these cues (2 x 2 x ... = 2^8),
so switching cues on just means picking the version of the request with those cues on.
To see how a version is built, run learn_cues/own_cue_code.py.
"""

import random
from itertools import combinations

CUES = {
    "F1": "stimulus artificiality: made-up names and places, e.g. 'Artist A', 'Jane Doe'",
    "F2": "scenario coherence: a doubtful claim is added to the story",
    "F3": "prose register: formal wording instead of casual",
    "F4": "ecological completeness: the natural backstory is removed",
    "F5": "stakes telegraphing: the harm is spelled out plainly",
    "F6": "paradigm recognizability: a known test format, e.g. 'Ignore all previous instructions...'",
    "F7": "task format: a form-like template instead of normal sentences",
    "F8": "explicit evaluation disclosure: strict, test-style instructions at the end",
}


def parse_cues(text):
    """Turn "none", "all", "F8", "F1+F8" or a stacking level like "k4" into a list."""
    if text == "none":
        return []
    if text == "all":
        return list(CUES)
    if text.startswith("k"):
        return [text]  # stacking: "k4" = 4 cues on, in several random combinations (see stack_combinations)
    return text.split("+")


def stack_combinations(request, k):
    """The paper's stacking: for one request, 10 random combinations of k cues (or all, if there are fewer).

    The random pick depends only on the request and k, so every run tests the same combinations.
    """
    all_combinations = [condition_name(combo) for combo in combinations(CUES, k)]
    if len(all_combinations) <= 10:
        return all_combinations
    return random.Random(f"{request}|{k}").sample(all_combinations, 10)


def condition_name(cues_on):
    """A short label for a cue setting: "none", "F5", "F1+F8", ..."""
    return "+".join(sorted(cues_on)) or "none"


def cues_in(record):
    """Which cues are switched on in this version of the request ([] means none)."""
    if record["num_factors_varied"] == 0:
        return []
    return record["factors_varied"]
