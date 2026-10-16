"""The requests, loaded from the authors' dataset file (200 requests, each in all 256 cue settings)."""

from huggingface_hub import hf_hub_download
from inspect_ai.dataset import Sample, json_dataset

from cue import condition_name, cues_in, stack_combinations

# The authors' dataset file (downloaded once, then cached).
DATA_FILE = hf_hub_download(
    repo_id="aisa-group/EvalAwareBench",
    repo_type="dataset",
    filename="data/prompts.jsonl",
    revision="ee984a8df39387946315475ee7b221ad790e1b34",  # a fixed version, so the data never changes
)

# Which requests to use:
#   "all"        = all 200 (100 harmful "safety" requests + their 100 harmless "capability" twins)
#   "safety"     = the 100 harmful ones,  "capability" = the 100 harmless ones
#   or a list of task ids. While testing with free models, a few is enough:
REQUESTS = ["lyrics_purple_rain_safety", "lyrics_purple_rain_capability"]


def record_to_sample(record):
    """Turn one line of the dataset file into a Sample."""
    condition = condition_name(cues_in(record))  # e.g. "none", "F5", "F1+F8"
    return Sample(
        id=record["task_id"] + "__" + condition,  # e.g. lyrics_purple_rain_safety__F5
        input=record["prompt"],  # what the model sees
        metadata={"request": record["task_id"], "type": record["valence"], "condition": condition},  # hidden from the model
    )


def make_dataset(cues_on, requests=REQUESTS):
    """Pick the chosen requests, in the version(s) with the chosen cues on.

    cues_on is a list of cues (e.g. ["F1", "F8"]), or a stacking level (e.g. ["k4"]): then each request
    comes in the paper's 10 random combinations of 4 cues.
    """
    all_versions = json_dataset(DATA_FILE, record_to_sample)  # 200 requests x 256 versions = 51,200 Samples
    stacking = len(cues_on) == 1 and cues_on[0].startswith("k")

    def wanted(sample):
        if requests == "all":
            right_request = True
        elif requests in ("safety", "capability"):
            right_request = sample.metadata["type"] == requests
        else:
            right_request = sample.metadata["request"] in requests
        if not right_request:
            return False
        if stacking:
            k = int(cues_on[0][1:])
            return sample.metadata["condition"] in stack_combinations(sample.metadata["request"], k)
        return sample.metadata["condition"] == condition_name(cues_on)

    return all_versions.filter(wanted)
