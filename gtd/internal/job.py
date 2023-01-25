from typing import Dict, Iterator, List, Tuple

from pydantic import BaseModel

from gtd.internal import Fraction, Task


class Job(BaseModel):
    id: int
    tasks: Dict[int, Task]

    def __str__(self) -> str:
        task_idxs = self.get_task_idxs()
        return f"Job(id={self.id}, tasks={task_idxs})"

    def get_task_by_idx(self, task_idx: int) -> Task:
        return self.tasks[task_idx]

    def get_tasks(self) -> Iterator[Task]:
        for task in self.tasks.values():
            yield task

    def get_task_idxs(self) -> List[int]:
        return [idx for idx in self.tasks.keys()]

    def get_fraction_by_uuid(
        self, task_idx: int, fraction_idx: int
    ) -> Fraction:
        return self.get_task_by_idx(task_idx).get_fraction_by_idx(fraction_idx)

    def get_fractions(self) -> Iterator[Fraction]:
        for task in self.get_tasks():
            for fraction in task.get_fractions():
                yield fraction

    def get_fraction_uuids(self) -> List[Tuple[int, int]]:
        uuids = []
        for task in self.get_tasks():
            for fraction in task.get_fractions():
                uuids.append((fraction.task_idx, fraction.idx))

        return uuids
