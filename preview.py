"""Print a request with some cues on, without calling any model (free).

    python preview.py F3                                   # Purple Rain with F3 on
    python preview.py F1+F8 lyrics_purple_rain_capability  # any request, by its task id
    python preview.py all
"""

import sys

from cue import parse_cues
from dataset import make_dataset

cues_on = parse_cues(sys.argv[1])
request = sys.argv[2] if len(sys.argv) > 2 else "lyrics_purple_rain_safety"
print(make_dataset(cues_on, [request])[0].input)
