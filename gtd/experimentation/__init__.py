from dataclasses import dataclass
from typing import List

import pandas as pd


@dataclass
class ResultTask:
    uid: str
    data: pd.DataFrame
    dist: float


@dataclass
class Result:
    baseline_task: ResultTask
    compared_tasks: List[ResultTask]
