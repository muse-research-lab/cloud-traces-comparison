from dataclasses import dataclass
from typing import Dict, Iterator, List

import pandas as pd

from gtd.experimentation.task import Task


@dataclass
class InputTask:
    idx: int
    data: pd.DataFrame


class Job:
    def __init__(self, id: int, tasks: List[InputTask]):
        self._id = id
        self._tasks = {
            task.idx: Task(id, task.idx, task.data) for task in tasks
        }

    def __str__(self) -> str:
        task_idxs = self.get_tasks_idx()
        return f"Job(id={self._id}, tasks={task_idxs})"

    @property
    def id(self) -> int:
        return self._id

    @property
    def tasks(self) -> Iterator[Task]:
        for task in self._tasks.values():
            yield task

    def get_tasks_idx(self) -> List[int]:
        return [idx for idx in self._tasks.keys()]

    def get_task_by_idx(self, idx: int) -> Task:
        return self._tasks[idx]

    def get_tasks_fraction(
        self, llim: int, ulim: int, copy: bool = True
    ) -> Dict[str, pd.DataFrame]:
        task_dict = {}
        for task in self.tasks:
            key = f"{task.job_id}-{task.idx}"
            task_dict[key] = task.get_fraction(llim, ulim, copy)

        return task_dict
